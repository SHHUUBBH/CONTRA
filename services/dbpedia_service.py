"""
DBpedia service for accessing structured knowledge via SPARQL queries.
"""

import logging
from typing import Dict, List, Any, Optional
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions

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
        self.sparql = SPARQLWrapper(endpoint)
        self.sparql.setReturnFormat(JSON)
        # Add timeout to prevent hanging on slow connections
        self.sparql.setTimeout(10)  # 10 seconds timeout
    
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
        
        try:
            # First find the resource URI
            resource_uri = self._find_resource_uri(topic)
            if not resource_uri:
                logger.warning(f"No DBpedia entry found for '{topic}'")
                return {
                    "success": False,
                    "error": f"No DBpedia entry found for '{topic}'."
                }
            
            # Then fetch detailed data
            data = self._fetch_resource_data(resource_uri)
            data["resource_uri"] = resource_uri
            data["success"] = True
            return data
            
        except SPARQLExceptions.EndPointInternalError as e:
            logger.error(f"DBpedia endpoint internal error: {str(e)}")
            return {
                "success": False,
                "error": f"DBpedia service is experiencing issues.",
                "details": str(e)
            }
        except SPARQLExceptions.QueryBadFormed as e:
            logger.error(f"DBpedia query syntax error: {str(e)}")
            return {
                "success": False,
                "error": f"Invalid query for DBpedia service.",
                "details": str(e)
            }
        except SPARQLExceptions.EndPointNotFound as e:
            logger.error(f"DBpedia endpoint not found: {str(e)}")
            return {
                "success": False,
                "error": f"DBpedia service is currently unavailable.",
                "details": str(e)
            }
        except SPARQLExceptions.Unauthorized as e:
            logger.error(f"DBpedia unauthorized: {str(e)}")
            return {
                "success": False,
                "error": f"Unauthorized access to DBpedia service.",
                "details": str(e)
            }
        except Exception as e:
            logger.error(f"DBpedia query failed: {str(e)}")
            return {
                "success": False,
                "error": f"DBpedia query failed.",
                "details": str(e)
            }
    
    def _find_resource_uri(self, topic: str) -> Optional[str]:
        """
        Find the DBpedia resource URI for a given topic.
        
        Args:
            topic: Topic name/keyword
            
        Returns:
            Resource URI or None if not found
        """
        # Escape quotes in the topic for the SPARQL query
        topic_safe = topic.replace('"', '\\"')
        
        # Query to find resource by English label
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?resource WHERE {{
          ?resource rdfs:label "{topic_safe}"@en .
        }} LIMIT 1
        """
        
        # Try exact match first
        self.sparql.setQuery(query)
        try:
            results = self.sparql.query().convert()
            bindings = results.get("results", {}).get("bindings", [])
            
            if bindings:
                return bindings[0]['resource']['value']
                
            # If no exact match, try a more flexible search
            query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?resource ?label WHERE {{
              ?resource rdfs:label ?label .
              FILTER(LANG(?label) = 'en') .
              FILTER(REGEX(?label, "{topic_safe}", "i")) .
            }} LIMIT 5
            """
            
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            bindings = results.get("results", {}).get("bindings", [])
            
            if bindings:
                return bindings[0]['resource']['value']
                
        except Exception as e:
            logger.error(f"Error finding DBpedia resource: {str(e)}")
        
        return None
    
    def _fetch_resource_data(self, resource_uri: str) -> Dict[str, Any]:
        """
        Fetch detailed data for a DBpedia resource.
        
        Args:
            resource_uri: DBpedia resource URI
            
        Returns:
            Dictionary with abstract, categories, etc.
        """
        # Query for abstract and categories
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT 
          ?abstract 
          (GROUP_CONCAT(DISTINCT ?cat; separator="; ") AS ?categories)
          (GROUP_CONCAT(DISTINCT ?type; separator="; ") AS ?types)
        WHERE {{
          <{resource_uri}> dbo:abstract ?abstract .
          FILTER(LANG(?abstract) = 'en') .
          
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
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        bindings = results.get("results", {}).get("bindings", [])
        
        if not bindings:
            return {"abstract": None, "categories": [], "types": []}
        
        # Extract data
        data = bindings[0]
        abstract = data.get('abstract', {}).get('value', '') if 'abstract' in data else ''
        
        # Parse categories and types
        categories = []
        if 'categories' in data and data['categories'].get('value'):
            # Split the concatenated string and clean category names
            cats_raw = data['categories']['value'].split('; ')
            categories = [clean_text(cat) for cat in cats_raw if cat]
        
        types = []
        if 'types' in data and data['types'].get('value'):
            # Split the concatenated string and clean type names
            types_raw = data['types']['value'].split('; ')
            types = [clean_text(type_) for type_ in types_raw if type_]
        
        return {
            "abstract": clean_text(abstract),
            "categories": categories,
            "types": types
        }
    
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
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?entity ?label ?relation WHERE {{
          {{
            <{resource_uri}> ?relation ?entity .
            ?entity rdfs:label ?label .
            FILTER(LANG(?label) = 'en') .
            FILTER(REGEX(STR(?relation), "^http://dbpedia.org/ontology/")) .
          }} UNION {{
            ?entity ?relation <{resource_uri}> .
            ?entity rdfs:label ?label .
            FILTER(LANG(?label) = 'en') .
            FILTER(REGEX(STR(?relation), "^http://dbpedia.org/ontology/")) .
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
                
                # Extract relation name from URI
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