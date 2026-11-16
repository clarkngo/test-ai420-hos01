"""Plan-and-execute (Understand & Refine): write this one by hand, no AI.

Build root_agent as a SequentialAgent of three agents: a planner with no
tools that writes 2-4 steps (output_key="plan"), an executor that follows
{plan} with the tools (output_key="findings"), and a writer that answers
from {findings} alone. The HOS 1 guide has the outline.

Reuse the tools:  from research_agent.tools import search_wikipedia, wikipedia_intro, calculate
"""

# TODO (Understand & Refine): define root_agent.
