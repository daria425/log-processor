from pydantic import BaseModel, Field, ConfigDict
from typing import List


class ErrorPattern(BaseModel):
    category: str = Field(
        ..., description="Category of the error, e.g. 'Database Error', 'Timeout Error', etc.")
    affected_endpoint: str = Field(
        ..., description="The API endpoint that is affected by this error.")
    root_cause: str = Field(
        ..., description="The underlying cause of the error, e.g. 'Connection refused', 'Query timeout', etc.")
    severity: str = Field(
        ..., description="Inferred severity level of the error, e.g. 'critical', 'high', 'medium', 'low'.")
    recommended_action: str = Field(
        ..., description="Recommended action to resolve the error, e.g. 'Restart database server', 'Optimize query', etc.")


class BatchSummary(BaseModel):
    patterns: List[ErrorPattern]
