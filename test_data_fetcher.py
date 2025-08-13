import sys
import json
import logging
from core.data_fetcher import data_fetcher
from models.data_model import TopicData

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def test_data_fetcher(topic):
    """Test the data fetcher directly with a given topic."""
    print(f"\n\n{'=' * 50}")
    print(f"TESTING DATA FETCHER FOR TOPIC: {topic}")
    print(f"{'=' * 50}\n")
    
    try:
        # Call the fetch_topic_data method
        print("Calling data_fetcher.fetch_topic_data...")
        data_result = data_fetcher.fetch_topic_data(topic)
        
        # Print information about the result
        print(f"\nData result type: {type(data_result)}")
        
        if hasattr(data_result, 'keys'):
            print(f"Data result keys: {list(data_result.keys())}")
            
            # Check the success flag
            success = data_result.get('success', False)
            print(f"Success: {success}")
            
            # Examine the data
            if 'data' in data_result:
                data = data_result['data']
                print(f"Data type: {type(data)}")
                
                if isinstance(data, TopicData):
                    print(f"TopicData object info:")
                    print(f"  - Topic: {data.topic}")
                    print(f"  - Wikipedia summary available: {bool(data.wikipedia and hasattr(data.wikipedia, 'summary') and data.wikipedia.summary)}")
                    print(f"  - DBpedia data available: {bool(data.dbpedia and hasattr(data.dbpedia, 'abstract') and data.dbpedia.abstract)}")
                    print(f"  - News articles: {len(data.news) if hasattr(data, 'news') else 'N/A'}")
                    
                    print("\nTesting .to_dict() method...")
                    try:
                        dict_result = data.to_dict()
                        print(f"to_dict() successful: {bool(dict_result)}")
                        print(f"Dictionary keys: {list(dict_result.keys())}")
                    except Exception as e:
                        print(f"to_dict() error: {e}")
                else:
                    print(f"Data is not a TopicData object. Details: {data}")
            else:
                print("No 'data' key in result")
                
            # Check for errors
            if 'errors' in data_result and data_result['errors']:
                print(f"Errors: {data_result['errors']}")
        else:
            print(f"Data result is not a dictionary: {data_result}")
    
    except Exception as e:
        print(f"\nEXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test with topics that work and don't work
    test_data_fetcher("malaria")
    test_data_fetcher("mahabharat") 