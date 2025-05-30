from app.schema.llm.tool import (
    AbstractTool,
    ToolSchema,
    ToolFunction,
    ToolFunctionParameters,
    ToolParameterProperty,
)
from typing import Callable, ClassVar
from app.schema.langgraph.tools.pubmed import (
    PubmedAbstractQuery,
    AbstractPubmedResult,
    PubmedAbstractsSet,
)
from app.core.logger import logger
import requests
import json


class SearchOpenAccessPubmedAbstracts(AbstractTool):
    """Tool for searching PubMed abstracts"""

    # Define the schema as a class variable with type annotation
    tool_schema: ClassVar[ToolSchema] = ToolSchema(
        type="function",
        function=ToolFunction(
            name="SearchOpenAccessPubmedAbstracts",
            description="Search PubMed for open access abstracts matching the given pubmed_query. Returns abstracts with metadata.",
            parameters=ToolFunctionParameters(
                type="object",
                properties={
                    "query": ToolParameterProperty(
                        type="string",
                        description="The search query string to find relevant papers",
                    ),
                    "page_size": ToolParameterProperty(
                        type="integer",
                        description="Number of results to return",
                        minimum=1,
                        maximum=100,
                        default=10,
                    ),
                    "cursor_mark": ToolParameterProperty(
                        type="string", description="Cursor for pagination", default="*"
                    ),
                    "result_type": ToolParameterProperty(
                        type="string",
                        description="Type of results to return",
                        default="core",
                    ),
                    "format": ToolParameterProperty(
                        type="string", description="Response format", default="json"
                    ),
                },
                required=["query"],
            ),
        ),
    )

    @classmethod
    def tool_function(cls) -> Callable:
        return cls.search_open_access_pubmed_abstracts

    @classmethod
    async def search_open_access_pubmed_abstracts(
        cls,
        query: str,
        page_size: int = 10,
        cursor_mark: str = "*",
        result_type: str = "core",
        format: str = "json",
    ) -> PubmedAbstractsSet:
        """
        Search PubMed for abstracts matching the given pubmed_query.
        """
        logger.info(f"Received search query: {query}")

        try:
            pubmed_query = PubmedAbstractQuery(
                query=query,
                page_size=page_size,
                cursor_mark=cursor_mark,
                result_type=result_type,
                format=format,
            )
        except Exception as e:
            logger.error(f"Failed to construct PubmedAbstractQuery: {str(e)}")
            raise

        base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        results = []
        cursor_mark = "*"  # Initial cursor mark to start pagination
        abstracts_retrieved = 0

        logger.info(
            f"Starting abstract retrieval with page_size={pubmed_query.page_size}"
        )

        while abstracts_retrieved < pubmed_query.page_size:
            params = {
                "query": f"OPEN_ACCESS:Y AND HAS_ABSTRACT:Y AND ({pubmed_query.query})",
                "pageSize": min(25, pubmed_query.page_size - abstracts_retrieved),
                "resultType": "core",
                "format": "json",
                "cursorMark": cursor_mark,
            }
            logger.debug(f"Making API request with params: {params}")

            try:
                response = requests.get(base_url, params=params)
                logger.debug(f"API response status code: {response.status_code}")

                if response.status_code != 200:
                    error_msg = f"Error fetching data: {response.status_code}"
                    logger.error(f"{error_msg}, Response: {response.text}")
                    raise Exception(error_msg)

                data = response.json()
                logger.debug("Successfully parsed response JSON")

                articles = data.get("resultList", {}).get("result", [])
                logger.info(f"Retrieved {len(articles)} articles in this batch")

                for article in articles:
                    try:
                        # Extract abstract text safely
                        abstract_text = article.get("abstractText", "")
                        if not abstract_text:
                            logger.warning(
                                f"Article {article.get('id', 'unknown')} has no abstract text, skipping"
                            )
                            continue

                        # Create base fields required by Citation
                        citation_fields = {
                            "utility": "Pending LLM evaluation",  # Placeholder until LLM evaluation
                            "abstract": abstract_text,
                            "full_text": "",  # Will be populated later if needed
                            "metadata": article,  # Store full article data as metadata
                            "id": article.get("id", ""),
                            "relevance_score": 0.0,  # Will be set by LLM later
                        }

                        # Merge citation fields with article data
                        result_data = {**article, **citation_fields}

                        # Create AbstractPubmedResult with all required fields
                        result = AbstractPubmedResult(**result_data)
                        results.append(result)
                        logger.debug(
                            f"Successfully processed article ID: {result.id}, Title: {result.title}"
                        )

                    except Exception as e:
                        logger.error(
                            f"Failed to process article {article.get('id', 'unknown')}: {str(e)}"
                        )
                        logger.debug(f"Article data: {json.dumps(article, indent=2)}")
                        continue

                abstracts_retrieved += len(articles)
                logger.info(
                    f"Total abstracts retrieved so far: {abstracts_retrieved}/{pubmed_query.page_size}"
                )

                if abstracts_retrieved >= pubmed_query.page_size:
                    logger.info("Reached desired number of abstracts")
                    break

                new_cursor_mark = data.get("nextCursorMark", cursor_mark)
                if new_cursor_mark == cursor_mark or not articles:
                    logger.info("No more results available or cursor hasn't changed")
                    break

                cursor_mark = new_cursor_mark
                logger.debug(f"Updated cursor mark: {cursor_mark}")

            except Exception as e:
                logger.error(f"Error during API request: {str(e)}")
                break

        logger.info(f"Search completed. Retrieved {len(results)} total abstracts")
        return PubmedAbstractsSet(abstracts=results)
