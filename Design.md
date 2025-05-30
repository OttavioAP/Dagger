
The stack I chose for this project is React/Next.js/FastAPI.

The primary libraries I used were:
HeyAPI.dev to autogen backend API route callers and types
Pydantic for backend data validation
Langgraph for workflows
Openrouter for LLM call API
React Flow for task graphing
SQLAlchemy for ORM. 

I enjoyed the creative aspect of this challenge, and appreciate any opportunity to play with trees. I chose to organize
the users tasks as a Directed Acyclic Graph. This allows me to determine the users highest priority task algorithmically, 
assuming the users priority is to avoid missing high priority deadlines. Users can also manage the dependency relationships between their tasks, and tasks from other workers on their team. This makes it easier to see how and why you're blocked.


I implemented a chatbot with access to both semantic and standard search
functions of the users past weeks. I chose to go with Langgraph for the rigid workflow to create summaries and feedback, and chat + tools for the more flexible search task.

I implemented 4 all-time productivity metrics. Deadlines misses, tasks completed, top collaborators and points scored.

I also generated a synthetic data set to test and demonstrate the 1024 dimension rag system used to chat with a users past. 

I also dockerized the backend/frontend and db, allowing another developer to run the service in a single command.