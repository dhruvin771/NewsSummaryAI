import os
import json
import re
from pymongo import MongoClient
import google.generativeai as genai
from typing import Dict, Any, List, Optional

class SmartGeminiMongoBot:
    def __init__(self, mongo_uri: str, db_name: str, collection_name: str, gemini_api_key: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def is_database_related(self, query: str) -> bool:
        """Check if query needs database lookup"""
        db_keywords = [
            'find', 'search', 'get', 'show', 'list', 'count', 'how many',
            'data', 'record', 'document', 'collection', 'database',
            'users', 'products', 'orders', 'items', 'entries'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in db_keywords)
    
    def extract_limit(self, query: str) -> int:
        """Extract limit from query like 'only 1', 'first 5', etc."""
        patterns = [
            r'only (\d+)',
            r'first (\d+)',
            r'top (\d+)',
            r'(\d+) only',
            r'limit (\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return int(match.group(1))
        
        return 10  # default limit
    
    def build_dynamic_query(self, user_query: str) -> Dict[str, Any]:
        """Build MongoDB query based on user input"""
        query = {}
        
        # Extract specific field searches
        if 'name' in user_query.lower():
            name_match = re.search(r'name.*?["\']([^"\']+)["\']|name.*?(\w+)', user_query.lower())
            if name_match:
                search_term = name_match.group(1) or name_match.group(2)
                query['name'] = {'$regex': search_term, '$options': 'i'}
        
        if 'email' in user_query.lower():
            email_match = re.search(r'email.*?["\']([^"\']+)["\']|email.*?(\S+@\S+)', user_query.lower())
            if email_match:
                search_term = email_match.group(1) or email_match.group(2)
                query['email'] = {'$regex': search_term, '$options': 'i'}
        
        if 'status' in user_query.lower():
            status_match = re.search(r'status.*?["\']([^"\']+)["\']|status.*?(\w+)', user_query.lower())
            if status_match:
                search_term = status_match.group(1) or status_match.group(2)
                query['status'] = {'$regex': search_term, '$options': 'i'}
        
        # If no specific fields found, use text search
        if not query:
            words = [word for word in user_query.split() if len(word) > 2]
            if words:
                query = {'$text': {'$search': ' '.join(words)}}
        
        return query
    
    def search_mongodb(self, user_query: str) -> List[Dict[str, Any]]:
        """Smart MongoDB search with dynamic queries"""
        limit = self.extract_limit(user_query)
        mongo_query = self.build_dynamic_query(user_query)
        
        try:
            if '$text' in mongo_query:
                results = list(self.collection.find(
                    mongo_query,
                    {'score': {'$meta': 'textScore'}}
                ).sort([('score', {'$meta': 'textScore'})]).limit(limit))
            else:
                results = list(self.collection.find(mongo_query).limit(limit))
            
            # Fallback if no results
            if not results:
                results = list(self.collection.find().limit(limit))
            
            return results
            
        except Exception as e:
            return list(self.collection.find().limit(limit))
    
    def format_context(self, documents: List[Dict[str, Any]]) -> str:
        """Format MongoDB documents for Gemini"""
        if not documents:
            return "No data found in database."
        
        context = f"Found {len(documents)} document(s) in database:\n\n"
        
        for i, doc in enumerate(documents, 1):
            doc_copy = doc.copy()
            if '_id' in doc_copy:
                del doc_copy['_id']
            context += f"Record {i}: {json.dumps(doc_copy, indent=2)}\n\n"
        
        return context
    
    def ask_gemini(self, user_question: str) -> str:
        """Process user question - check DB relevance first"""
        
        # Check if question needs database lookup
        if not self.is_database_related(user_question):
            # Answer directly without database
            try:
                response = self.model.generate_content(f"Answer this question directly: {user_question}")
                return response.text
            except Exception as e:
                return f"Error: {str(e)}"
        
        # Database-related question
        mongo_docs = self.search_mongodb(user_question)
        context = self.format_context(mongo_docs)
        
        prompt = f"""{context}
User Question: {user_question}

Answer based on the database records above. Be specific and direct."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def close_connection(self):
        self.client.close()

def main():
    MONGO_URI = "mongodb://localhost:27017/"
    DB_NAME = "your_database"
    COLLECTION_NAME = "your_collection"
    GEMINI_API_KEY = "your_gemini_api_key"
    
    bot = SmartGeminiMongoBot(MONGO_URI, DB_NAME, COLLECTION_NAME, GEMINI_API_KEY)
    
    print("Smart Gemini + MongoDB Bot Ready!")
    print("Examples:")
    print("- 'find only 1 user named john'")
    print("- 'show first 3 products'") 
    print("- 'what is the weather like?' (non-DB question)")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("Ask me: ")
        
        if user_input.lower() == 'quit':
            break
        
        answer = bot.ask_gemini(user_input)
        print(f"\nAnswer: {answer}\n" + "="*50)
    
    bot.close_connection()

if __name__ == "__main__":
    main()