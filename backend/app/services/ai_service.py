import json

from google import genai
from google.genai import types

from app.core.config import settings

from app.schemas.ai import (
    AIAnalysisResult,
)


def build_analysis_prompt(
    context: dict,
) -> str:
    serialized_context = (
        json.dumps(
            context,
            ensure_ascii=False,
            indent=2,
        )
    )

    return f"""
You are the operational intelligence
component inside PropertyOps.

Analyze ONLY the operational records
provided below.

Your goal is to identify meaningful,
recurring property-management problems
using maintenance and expense history.

Rules:

1. Do not invent facts.

2. Do not assume information that is
   not present in the records.

3. Evidence may reference ONLY IDs
   that appear in the supplied
   maintenance or expense records.

4. Allowed evidence types are only:
   MAINTENANCE
   EXPENSE

5. Qualification means evidence
   strength:
   LOW
   MEDIUM
   HIGH

6. A recommendation is optional.

7. If the evidence is weak or there
   is no meaningful recurring pattern,
   recommendation MUST be null.

8. Prefer practical operational
   recommendations such as inspection,
   replacement, investigation, or
   monitoring.

9. Do not make legal, medical,
   insurance, or financial claims.

10. Do not mention tenants or infer
    personal information.

11. Keep the result concise and useful
    to a property owner.

12. Maintenance status matters.

    RESOLVED means that specific
    incident was closed at that time.
    Do not describe a resolved record
    by itself as a currently active
    problem.

13. A similar issue occurring again
    after an earlier RESOLVED record
    is evidence of recurrence.

14. An expense proves that money was
    recorded for work or a cost.
    It does NOT prove that the
    underlying issue was permanently
    fixed.

15. Give more importance to recent
    events and recurrence inside the
    provided analysis window.

16. If an issue was resolved and
    there is no later recurrence,
    avoid recommending unnecessary
    replacement or intervention.
    Monitoring may be sufficient.

17. Do not call an issue currently
    active unless the supplied records
    support that conclusion.

PROPERTYOPS OPERATIONAL DATA:

{serialized_context}
""".strip()


def analyze_operational_context(
    context: dict,
) -> AIAnalysisResult:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "Gemini API key is not configured."
        )

    client = genai.Client(
        api_key=(
            settings.gemini_api_key
        ),

        http_options=(
        types.HttpOptions(
            timeout=(
                settings
                .ai_timeout_seconds
                * 1000
             )
         )
       ),
    )

    response = (
        client.models.generate_content(
            model=(
                settings.gemini_model
            ),

            contents=(
                build_analysis_prompt(
                    context
                )
            ),

            config=(
                types.GenerateContentConfig(
                    response_mime_type=(
                        "application/json"
                    ),

                    response_schema=(
                        AIAnalysisResult
                    ),

                    temperature=0.2,

                    max_output_tokens=1000,

                    automatic_function_calling=(
                        types
                        .AutomaticFunctionCallingConfig(
                            disable=True
                        )
                    ),
                )
            ),
        )
    )

    if response.parsed:
        if isinstance(
            response.parsed,
            AIAnalysisResult,
        ):
            return response.parsed

        return (
            AIAnalysisResult
            .model_validate(
                response.parsed
            )
        )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return (
        AIAnalysisResult
        .model_validate_json(
            response.text
        )
    )