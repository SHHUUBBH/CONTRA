"""
DBpedia service for accessing structured knowledge via SPARQL queries.
"""

import logging
import urllib.parse
from typing import Dict, List, Any, Optional

try:
    from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
    HAS_SPARQL = True
except ImportError:
    HAS_SPARQL = False
    SPARQLWrapper = None
    JSON = None
    SPARQLExceptions = None

from utils.cache import disk_cache
from utils.helpers import clean_text

# Configure logging
logger = logging.getLogger(__name__)


class DBpediaService:
    """
    Service for accessing DBpedia knowledge via SPARQL queries.
    DBpedia (https://wiki.dbpedia.org/) provides structured data extracted from Wikipedia.
    """
    
    def __init__(self, endpoint: str = "http://dbpedia.org/sparql"):
        """
        Initialize the DBpedia service.
        
        Args:
            endpoint: SPARQL endpoint URL
        """
        self.endpoint = endpoint
        if HAS_SPARQL and SPARQLWrapper:
            self.sparql = SPARQLWrapper(endpoint)
            self.sparql.setReturnFormat(JSON)
            # Add timeout to prevent hanging on slow connections
            self.sparql.setTimeout(8)  # 8 seconds timeout
        else:
            self.sparql = None
    
    @disk_cache(subdir='dbpedia')
    def get_data(self, topic: str) -> Dict[str, Any]:
        """
        Query DBpedia for structured data about a topic.
        
        Args:
            topic: Topic name/keyword
            
        Returns:
            Dictionary with abstract, categories, and other data
        """
        logger.info(f"Fetching DBpedia data for: {topic}")
        
        if not self.sparql:
            return {
                "success": False,
                "error": "SPARQL service not initialized.",
                "abstract": "",
                "categories": [],
                "types": []
            }
        
        try:
            # First find the resource URI
            resource_uri = self._find_resource_uri(topic)
            if not resource_uri:
                logger.warning(f"No DBpedia entry found for '{topic}'")
                return {
                    "success": False,
                    "error": f"No DBpedia entry found for '{topic}'.",
                    "abstract": "",
                    "categories": [],
                    "types": []
                }
            
            # Then fetch detailed data
            data = self._fetch_resource_data(resource_uri)
            data["resource_uri"] = resource_uri
            data["success"] = True
            return data
            
        except Exception as e:
            logger.error(f"DBpedia query failed: {str(e)}")
            return {
                "success": False,
                "error": f"DBpedia query failed.",
                "details": str(e),
                "abstract": "",
                "categories": [],
                "types": []
            }
    
    def _find_resource_uri(self, topic: str) -> Optional[str]:
        """
        Find the DBpedia resource URI for a given topic quickly without full-table scans.
        
        Args:
            topic: Topic name/keyword
            
        Returns:
            Resource URI or None if not found
        """
        if not self.sparql or not topic or not topic.strip():
            return None

        # Clean topic and produce candidate resource names
        cleaned_topic = topic.strip()
        safe_candidates = [
            cleaned_topic.replace(' ', '_'),
            cleaned_topic.capitalize().replace(' ', '_'),
            cleaned_topic.title().replace(' ', '_')
        ]
        # Remove duplicates while preserving order
        candidates = list(dict.fromkeys(safe_candidates))
        
        # 1. Quick check: check candidate URIs directly (including Wikipedia redirects)
        for cand in candidates:
            cand_uri = f"http://dbpedia.org/resource/{urllib.parse.quote(cand)}"
            try:
                # Check for redirects first
                redirect_query = f"""
                PREFIX dbo: <http://dbpedia.org/ontology/>
                SELECT ?redirect WHERE {{
                  <{cand_uri}> dbo:wikiPageRedirects ?redirect .
                }} LIMIT 1
                """
                self.sparql.setQuery(redirect_query)
                res = self.sparql.query().convert()
                bindings = res.get("results", {}).get("bindings", [])
                if bindings and 'redirect' in bindings[0]:
                    return bindings[0]['redirect']['value']

                # Check if candidate exists directly
                ask_query = f"ASK {{ <{cand_uri}> ?p ?o }}"
                self.sparql.setQuery(ask_query)
                ask_res = self.sparql.query().convert()
                if ask_res.get('boolean') is True:
                    return cand_uri
            except Exception as e:
                logger.debug(f"Candidate check failed for {cand_uri}: {e}")

        # 2. Query to find resource by exact English label
        topic_safe = cleaned_topic.replace('"', '\\"')
        label_query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?resource WHERE {{
          {{ ?resource rdfs:label "{topic_safe}"@en }}
          UNION
          {{ ?resource rdfs:label "{topic_safe.capitalize()}"@en }}
          UNION
          {{ ?resource rdfs:label "{topic_safe.title()}"@en }}
        }} LIMIT 1
        """
        try:
            self.sparql.setQuery(label_query)
            results = self.sparql.query().convert()
            bindings = results.get("results", {}).get("bindings", [])
            if bindings and 'resource' in bindings[0]:
                return bindings[0]['resource']['value']
        except Exception as e:
            logger.warning(f"Label query failed for DBpedia: {e}")
        
        return None
    
    def _fetch_resource_data(self, resource_uri: str) -> Dict[str, Any]:
        """
        Fetch detailed data for a DBpedia resource.
        
        Args:
            resource_uri: DBpedia resource URI
            
        Returns:
            Dictionary with abstract, categories, etc.
        """
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT 
          ?abstract ?comment ?desc
          (GROUP_CONCAT(DISTINCT ?cat; separator="; ") AS ?categories)
          (GROUP_CONCAT(DISTINCT ?type; separator="; ") AS ?types)
        WHERE {{
          OPTIONAL {{ <{resource_uri}> dbo:abstract ?abstract . FILTER(LANG(?abstract) = 'en') }}
          OPTIONAL {{ <{resource_uri}> rdfs:comment ?comment . FILTER(LANG(?comment) = 'en') }}
          OPTIONAL {{ <{resource_uri}> dbo:description ?desc . FILTER(LANG(?desc) = 'en') }}
          
          # Get categories
          OPTIONAL {{ 
            <{resource_uri}> dct:subject ?catResource . 
            ?catResource rdfs:label ?cat .
            FILTER(LANG(?cat) = 'en')
          }}
          
          # Get types
          OPTIONAL {{ 
            <{resource_uri}> a ?typeResource . 
            ?typeResource rdfs:label ?type .
            FILTER(LANG(?type) = 'en')
          }}
        }}
        """
        
        try:
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            bindings = results.get("results", {}).get("bindings", [])
            
            if not bindings:
                return {"abstract": "", "categories": [], "types": []}
            
            data = bindings[0]
            # Prioritize full abstract, then comment, then short description
            abstract = ""
            if 'abstract' in data and data['abstract'].get('value'):
                abstract = data['abstract']['value']
            elif 'comment' in data and data['comment'].get('value'):
                abstract = data['comment']['value']
            elif 'desc' in data and data['desc'].get('value'):
                abstract = data['desc']['value']
            
            # Parse categories and types
            categories = []
            if 'categories' in data and data['categories'].get('value'):
                cats_raw = data['categories']['value'].split('; ')
                categories = [clean_text(cat) for cat in cats_raw if cat]
            
            types = []
            if 'types' in data and data['types'].get('value'):
                types_raw = data['types']['value'].split('; ')
                types = [clean_text(type_) for type_ in types_raw if type_]
            
            return {
                "abstract": clean_text(abstract),
                "categories": categories,
                "types": types
            }
        except Exception as e:
            logger.error(f"Error fetching DBpedia resource data: {e}")
            return {"abstract": "", "categories": [], "types": []}
    
    @disk_cache(subdir='dbpedia')
    def get_related_entities(self, resource_uri: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find related entities for a given resource.
        
        Args:
            resource_uri: DBpedia resource URI
            limit: Maximum number of results
            
        Returns:
            List of related entities with their labels and types
        """
        if not self.sparql or not resource_uri:
            return []

        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?entity ?label ?relation WHERE {{
          {{
            <{resource_uri}> ?relation ?entity .
            ?entity rdfs:label ?label .
            FILTER(LANG(?label) = 'en') .
            FILTER(STRSTARTS(STR(?relation), "http://dbpedia.org/ontology/")) .
          }} UNION {{
            ?entity ?relation <{resource_uri}> .
            ?entity rdfs:label ?label .
            FILTER(LANG(?label) = 'en') .
            FILTER(STRSTARTS(STR(?relation), "http://dbpedia.org/ontology/")) .
          }}
        }} LIMIT {limit}
        """
        
        try:
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            bindings = results.get("results", {}).get("bindings", [])
            
            entities = []
            for binding in bindings:
                label = binding.get('label', {}).get('value', '')
                entity_uri = binding.get('entity', {}).get('value', '')
                relation = binding.get('relation', {}).get('value', '')
                relation_name = relation.split('/')[-1] if '/' in relation else relation
                
                entities.append({
                    "label": label,
                    "uri": entity_uri,
                    "relation": relation_name
                })
            
            return entities
            
        except Exception as e:
            logger.error(f"Error fetching related entities: {str(e)}")
            return []


# Create a singleton instance
dbpedia_service = DBpediaService()