"""
Firebase client for state management, real-time data streaming, and persistence.
Implements the CRITICAL requirement to use Firebase for all database needs.
"""
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor

import firebase_admin
from firebase_admin import credentials, firestore, db
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.collection import CollectionReference

from config import config

logger = logging.getLogger(__name__)

class FirebaseClient:
    """
    Firebase client wrapper with connection management, error handling, and retry logic.
    Supports both Firestore (for structured data) and Realtime Database (for streaming).
    """
    
    _instance: Optional['FirebaseClient'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize()
            self._initialized = True
    
    def _initialize(self) -> None:
        """Initialize Firebase connection with error handling."""
        try:
            # Check if Firebase app already exists
            if not firebase_admin._apps:
                if os.path.exists(config.database.credentials_path):
                    cred = credentials.Certificate(config.database.credentials_path)
                    firebase_admin.initialize_app(cred, {
                        'projectId': config.database.project_id,
                        'databaseURL': f'https://{config.database.project_id}.firebaseio.com'
                    })
                    logger.info(f"Firebase initialized for project: {config.database.project_id}")
                else:
                    raise FileNotFoundError(
                        f"Firebase credentials not found at {config.database.credentials_path}"
                    )
            else:
                logger.info("Firebase app already initialized")
            
            # Initialize clients