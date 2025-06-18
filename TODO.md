# 📋 Project Rules and Guidelines

## 🤖 AI Assistant Guidelines
- [x] All code recommendations should first explain why it's needed and what it will be done.
  _Done: We've been following this practice in our recent work, especially with ChromaDB implementation._
- [ ] All code changes must be reviewed before implementation
- [x] Each feature must include proper error handling
  _Done: Added comprehensive error handling in ChromaDB initialization and manual processing._
- [ ] Documentation must be updated with each significant change
- [ ] Security best practices must be followed for all API endpoints
- [x] Environment variables must be used for sensitive data
  _Done: Using environment variables for ChromaDB persist directory and other sensitive data._
- [ ] API responses must follow RESTful conventions
- [x] Code must be properly commented and documented
  _Done: Added detailed logging and comments in ChromaDB and manual processing code._
- [ ] Performance considerations must be addressed
- [x] Make a validation if a task has been completed, if so please tell me why do you consider it and if i agree please update TODO.md where it correspond
  _Done: We're doing this now with the ChromaDB implementation._

## 🎯 Development Standards
- [ ] Follow PEP 8 for Python code style
- [ ] Use type hints in Python code
- [ ] Implement proper exception handling
- [ ] Write meaningful commit messages
- [ ] Keep functions small and focused
- [ ] Use meaningful variable and function names
- [ ] Implement proper input validation
- [ ] Follow the DRY (Don't Repeat Yourself) principle
- [ ] Write self-documenting code
- [ ] Use async/await for I/O operations

## 🔒 Security Requirements
- [ ] Implement rate limiting for all endpoints
- [ ] Use HTTPS for all communications
- [ ] Implement proper authentication and authorization based on twilio signature and considering the interaction is by phone calls
- [ ] Sanitize all user inputs
- [ ] Follow OWASP security guidelines
- [ ] Implement proper session management based on system architecture
- [ ] Use secure password hashing based on system architecture
- [ ] Implement proper CORS policies
- [ ] Regular security audits
- [ ] Keep dependencies updated

## 📝 Documentation Requirements
- [ ] API documentation using OpenAPI/Swagger
- [ ] Clear README with setup instructions
- [ ] Code comments for complex logic
- [ ] Architecture diagrams
- [ ] Deployment documentation
- [ ] Troubleshooting guides
- [ ] API usage examples
- [ ] Environment setup guide
- [ ] Testing documentation
- [ ] Maintenance procedures

# 🧠 Project Description

I'm building an API-first SaaS product that acts as a voice technical support agent for LATAM companies. The system allows human operators to call a phone number and receive automated assistance based on each company's specific operation manuals.

## 🏗️ Main Components

- [ ] Real phone calls (via Twilio)
- [ ] Voice recognition and synthesis in Latin Spanish
- [ ] Multi-tenant backend in FastAPI
- [ ] Semantic ingestion and query of manuals per company (via ChromaDB and Langchain)
- [ ] LLM response generation (GPT-4), in natural language

## 🎯 General Objective
To offer a plug-and-play tool for companies with documented technical processes, where the bot acts as a "telephone sherpa" that guides the operator step by step according to the context.

## 🎯 Stage 1 Objective (Real MVP)
An operator dials a number → backend receives audio → transcription → client manual consultation → response generation → voice response.

# 🛠️ Work Plan: Stage 1 (Functional Technical MVP)

## Phase 1: Backend Base (FastAPI + minimal endpoints)
**Objective**: Set up a multi-client backend to receive transcription and respond

### 1.1 Project Setup and Structure
- [x] Set up app/ directory with core modules  
  _Done: app/ contains core/, api/, db/, models/, schemas/; config.py and main.py are set up and integrated._
- [ ] Configure logging and error handling
- [x] Set up environment configuration
- [x] Create base middleware for request/response handling  
  _Done: RequestIDMiddleware implemented in app/core/middleware.py and added to main.py._
- [x] Dockerize FastAPI app with Dockerfile
- [x] Add docker-compose.yml for app + Postgres
- [x] Add .dockerignore
- [x] Update README with Docker instructions

### 1.2 Multi-tenant Architecture
- [x] Implement tenant model and schema
  - [x] Create Tenant model with fields:
    - [x] id (UUID)
    - [x] name (String)
    - [x] api_key (String, hashed)
    - [x] created_at (DateTime)
    - [x] updated_at (DateTime)
    - [x] status (Enum: active, inactive)
  - [x] Create Pydantic schemas for:
    - [x] TenantCreate
    - [x] TenantUpdate
    - [x] TenantResponse
- [x] Implement tenant CRUD operations
  - [x] Create tenant repository/database operations  
    _Done: TenantRepository with CRUD methods implemented._
  - [x] Create tenant service layer  
    _Done: TenantService with business logic and data transformation._
  - [x] Create tenant API endpoints  
    _Done: REST endpoints for create, read, update, delete operations._
- [x] Implement tenant middleware
  - [x] Create tenant identification logic  
    _Done: TenantMiddleware extracts tenant ID from 'X-Tenant-ID' header._
  - [x] Add tenant context to requests  
    _Done: Tenant ID stored in request.state.tenant_id._
  - [x] Implement tenant validation  
    _Done: Basic logging added (validation logic to be expanded later)._
- [ ] Enhance tenant middleware
  - [ ] Add database validation (check if tenant exists)
  - [ ] Add status validation (check if tenant is active)
  - [ ] Add API key validation

### 1.3 Security Implementation
- [ ] Set up authentication
  - [ ] Implement API key validation (using tenant's API key)
  - [ ] Add request signing verification
  - [ ] Create security middleware
- [ ] Implement authorization
  - [ ] Add tenant-based access control
  - [ ] Create permission system
  - [ ] Implement role-based access

### 1.4 Core Endpoints
- [x] Implement /ask endpoint
  - [x] Create request schema for text input
  - [x] Add input validation
  - [ ] Implement rate limiting per tenant
  - [x] Add error handling
  - [x] Create response schema
  - [ ] Add request logging
- [x] Implement /manual/upload endpoint
  - [x] Create file upload handling
  - [x] Add file type validation (PDF)
  - [ ] Implement file size limits
  - [ ] Add tenant-specific storage
  - [x] Create upload response schema
  - [ ] Add upload logging

### 1.5 Testing Setup
- [ ] Set up testing framework
  - [ ] Configure pytest
  - [ ] Create test database
  - [ ] Add test fixtures
- [ ] Write initial tests
  - [ ] Test tenant creation/management
  - [ ] Test /ask endpoint
  - [ ] Test /manual/upload endpoint
  - [ ] Test security measures

### 1.6 Documentation
- [ ] API Documentation
  - [ ] Set up OpenAPI/Swagger
  - [ ] Document all endpoints
  - [ ] Add request/response examples
- [ ] Code Documentation
  - [ ] Add docstrings to all functions
  - [ ] Document complex logic
  - [ ] Create architecture diagrams

## Phase 2: Manual Ingestion and Search
**Objective**: Load manuals per client and perform contextual searches

### 2.1 PDF Processing Setup
- [x] Set up text chunking utilities
  - [x] Create ManualTextSplitter class
  - [x] Configure chunk size and overlap
  - [x] Implement text splitting logic
- [x] Set up embeddings management
  - [x] Create EmbeddingsManager class
  - [x] Configure OpenAI embeddings
  - [x] Implement async embedding generation
- [x] Set up ChromaDB storage
  - [x] Configure persistence directory
  - [x] Set up tenant-specific collections
  - [x] Implement vector storage logic
  _Done: Added detailed logging and error handling for ChromaDB initialization and storage._

### 2.2 Manual Processing Implementation
- [x] Implement PDF text extraction
  - [x] Add PDF validation (file type, size)
  - [x] Implement text extraction with error handling
  - [x] Add progress tracking for large files
  _Done: Implemented in ManualProcessor with progress tracking and error handling._
- [x] Implement text chunking
  - [x] Add metadata to chunks (page numbers, sections)
  - [x] Implement smart chunking (respect paragraphs, sections)
  - [x] Add chunk size optimization
  _Done: Implemented in ManualTextSplitter with configurable chunk size and overlap._
- [x] Implement embedding generation
  - [x] Add batch processing for large documents
  - [x] Implement retry logic for API failures
  - [x] Add embedding caching
  _Done: Implemented in EmbeddingsManager with async processing and error handling._

### 2.3 Storage and Retrieval
- [x] Implement ChromaDB storage
  - [x] Add tenant isolation
  - [x] Implement collection management
  - [x] Add storage optimization
  _Done: Implemented tenant-specific collections with proper isolation and management._
- [x] Implement semantic search
  - [x] Add relevance scoring
  - [x] Implement context window selection
  - [x] Add search result ranking
  _Done: Implemented semantic search with context windows, relevance scoring, and result ranking._
- [x] Add conversation context handling
  - [x] Implement conversation ID tracking
  - [x] Store conversation history per tenant
  - [x] Use conversation context to improve response relevance
  - [x] Add conversation cleanup/expiration
  _Done: Implemented ConversationStorage service with Redis cache, 24-hour TTL, and tenant isolation._
- [ ] Add data management
  - [ ] Implement manual versioning
  - [ ] Add manual update/delete operations
  - [ ] Implement storage cleanup

### 2.4 API Integration
- [ ] Update /manual/upload endpoint
  - [ ] Add file validation
  - [ ] Implement async processing
  - [ ] Add progress tracking
- [x] Update /ask endpoint
  - [x] Integrate semantic search
  - [x] Add context retrieval
  - [x] Implement response formatting
- [ ] Add manual management endpoints
  - [ ] Add manual listing
  - [ ] Add manual deletion
  - [ ] Add manual update

### 2.5 Testing and Optimization
- [ ] Add unit tests
  - [ ] Test PDF processing
  - [ ] Test text chunking
  - [ ] Test embedding generation
- [ ] Add integration tests
  - [ ] Test ChromaDB storage
  - [ ] Test semantic search
  - [ ] Test API endpoints
- [ ] Performance optimization
  - [ ] Optimize chunking strategy
  - [ ] Implement caching
  - [ ] Add batch processing

## Phase 3: GPT Response Generation
**Objective**: Combine relevant context from the manual with the operator's question to generate natural language responses

### 3.1 GPT Integration Setup
- [x] Set up OpenAI integration
  - [x] Add OpenAI API key configuration
  - [x] Create GPT client wrapper
  - [x] Implement error handling and retries
  - [ ] Add rate limiting and cost tracking

### 3.2 Prompt Engineering
- [x] Design base prompt for technical agent
  - [x] Create system prompt for technical support role
  - [x] Define context formatting guidelines
  - [x] Add response structure requirements
  - [x] Include fallback handling instructions
- [x] Implement prompt templates
  - [x] Create template for question answering
  - [x] Add context formatting template
  - [x] Include source attribution template
  - [x] Add error handling templates

### 3.3 Response Generation
- [x] Create RetrievalQA chain
  - [x] Set up Langchain integration
  - [x] Configure context retrieval
  - [x] Implement answer generation
  - [x] Add source tracking
- [x] Implement response processing
  - [x] Add answer validation
  - [x] Implement source attribution
  - [x] Add confidence scoring
  - [x] Handle edge cases
- [x] Integration with /ask Endpoint
  - [x] Modify request handling
  - [x] Add context preparation
  - [x] Implement response formatting
  - [x] Add error handling
- [x] Add response caching
  - [x] Implement cache storage
  - [x] Add cache invalidation
  - [x] Configure cache TTL
  - [x] Add cache hit/miss tracking
  _Done: Enhanced Cache class with Redis implementation, tag-based invalidation, TTL configuration, and statistics tracking._

### 3.4 Testing and Optimization
- [ ] Add unit tests
  - [ ] Test prompt templates
  - [ ] Test response generation
  - [ ] Test error handling
  - [ ] Test caching
- [ ] Add integration tests
  - [ ] Test end-to-end flow
  - [ ] Test with real manuals
  - [ ] Test error scenarios
  - [ ] Test performance
- [ ] Performance optimization
  - [ ] Optimize prompt size
  - [ ] Implement response streaming
  - [ ] Add parallel processing
  - [ ] Optimize caching strategy

## Phase 4: WhatsApp Cloud API Integration
**Objective**: Receive text messages from WhatsApp and respond with automated assistance

### 4.1 WhatsApp Cloud API Setup
- [x] Set up WhatsApp Cloud API account
  - [x] Create Meta Business account
    _Done: Business account created and test number obtained_
  - [x] Set up WhatsApp Cloud API
    _Done: API access configured with test number_
  - [x] Configure environment variables
    _Note: Added WhatsApp-related environment variables in config.py_
  - [ ] Set up billing information
    _Note: Required for production use, not needed for test number_
- [ ] Configure WhatsApp Cloud API number
  - [x] Verify business phone number
    _Done: Test number verified and active_
  - [x] Set up webhook URL
    _Done: Webhook URL configured and verified in Meta Developer Dashboard_
  - [ ] Add test phone numbers
    _Note: Need to add recipient phone numbers to allowed list_

### 4.2 Webhook Configuration
- [x] Configure webhook to FastAPI for incoming messages
  - [x] Create WhatsApp webhook endpoint
  - [x] Implement request validation
  - [x] Add Cloud API signature verification (simplified)
  - [x] Set up error handling
- [x] Implement message handling
  - [x] Create message state management
  - [x] Add text message processing
    _Done: Implemented in WhatsAppService with validation and error handling_
  - [x] Implement timeout handling
    _Note: Implemented for text messages with retry logic_
  - [x] Implement message status tracking
    _Note: Implemented tracking for sent, delivered, and read statuses_

### 4.3 Text Message Handling
- [x] Configure text message permissions
- [x] Set up text message settings
- [x] Implement text message validation
- [x] Add timeout handling
- [x] Implement error handling
- [x] Test text message receiving
- [ ] Add message length limits (optional)

### 4.4 Response Handling
- [x] Process text messages
  - [x] Send to /ask endpoint
  - [x] Handle response formatting
  - [x] Add error handling
  - [x] Implement retry logic
    _Done: Added integration with /ask endpoint, error handling, and retry logic_
- [x] Generate text response
  - [x] Configure response formatting
  - [x] Set up response parameters
  - [x] Add response validation
  - [x] Implement response caching
    _Done: Added response generation with proper formatting and caching_
- [x] Send WhatsApp response
  - [x] Implement message status tracking
  - [x] Add retry logic
  - [x] Handle delivery status
  - [x] Add error recovery

### 4.5 Testing and Monitoring
- [ ] Set up testing environment
  - [ ] Create test WhatsApp numbers
  - [ ] Set up test webhooks
  - [ ] Configure test credentials
- [ ] Implement monitoring
  - [ ] Add message logging
  - [ ] Set up error tracking
  - [ ] Monitor response quality
  - [ ] Track response times

## 🎯 Result of this stage
You'll have an environment where:
- [ ] The client uploads their manual
- [ ] An operator sends a voice message via WhatsApp
- [ ] The bot responds with a voice message based on that manual
- [ ] All logic lives in a backend controlled by you

## 🪜 Proposed daily breakdown (reference for 1 person)

| Day | Activity |
|-----|-----------|
| 1   | FastAPI setup + basic multi-tenant structure |
| 2   | Manual ingestion and embeddings + search testing |
| 3   | QA chain with Langchain + contextual response |
| 4   | Initial WhatsApp integration (text to text only) |
| 5   | Real voice message handling and end-to-end testing |