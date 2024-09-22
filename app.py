import streamlit as st
import openai
import pandas as pd  
import altair as alt  
import re

# Set OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Set Streamlit configuration and theme
st.set_page_config(layout="wide", page_title="AI Hackathon Planner")

# Customize theme using inline CSS
st.markdown(
    """
    <style>
        h1, h2 {color: #f200fe;}
        h3 {color: #f2baf7;}
    </style>
    """, 
    unsafe_allow_html=True
)

# Header
st.title("AI-Powered Hackathon Planner")
st.write("Simplify your hackathon planning with AI. Generate schedules, budgets, marketing strategies, and more.")

# Sidebar for Event Details
st.sidebar.markdown('<h2 style="color: #f2baf7;">Enter Event Details</h2>', unsafe_allow_html=True)

event_name = st.sidebar.text_input("Event Name", placeholder="Enter event name")
event_theme = st.sidebar.text_input("Event Theme", placeholder="Enter event theme")
event_date = st.sidebar.date_input("Event Date")

event_format = st.sidebar.selectbox("Format", ["Physical", "Virtual", "Hybrid"])
event_duration = st.sidebar.number_input("Duration (hours)", min_value=24, max_value=120, step=1)  # Custom duration
participants = st.sidebar.number_input("Number of Participants", min_value=30, step=1, format="%d")

# Predefined list of locations
locations = [
    "Kuala Lumpur, Malaysia",
    "New York, USA",
    "Tokyo, Japan",
    "London, UK",
    "Sydney, Australia",
    "Berlin, Germany",
    "Toronto, Canada",
    "Dubai, UAE",
    "Paris, France",
    "Mumbai, India"
]

# Sidebar for Event Location
event_location = st.sidebar.selectbox("Location", locations)

# Sidebar Button to Generate Planner
if st.sidebar.button("Generate Planner"):
    # Validation check
    if not event_name or not event_theme or not event_date:
        st.sidebar.error("Please fill in all event details before generating.")
    else:
        # Timetable Generation
        with st.spinner("Generating Schedule..."):
            timetable_prompt = f"""
            Generate a detailed timetable for a hackathon named '{event_name}' with the theme '{event_theme}'. The event will last {event_duration} hours, starting on {event_date}, and is {event_format}.

            - Format the timetable as a table only; do not include any additional text, outlines, or formatting.
            - If the event duration is 24 hours, create a single table for the entire day, labeled 'Day 1', 
            if the event duration is 48 hours, create two separate tables, one for each day, labeled 'Day 1' 
            and 'Day 2', and the list goes on.
            - Include the following columns in the table:
              - **Time** (e.g., '08:00 - 09:00'; ensure this is on a single line without any line breaks or extra spaces)
              - **Activity**
              - **Location** (generic, on a single line & format-dependent)
              - **Description** 
              - **Notes** 
            
            Use term "coding" not "hacking"

            Ensure that all cells in the table are filled with relevant information and that there are no placeholders like 'N/A'. 
            The table should be clean and straightforward, with all data on a single line per cell. The headings for each table 
            should be formatted (in font size: h3) as '{event_name} - Day 1' or '{event_name} - Day 2', based on the event duration.
            """
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": timetable_prompt}],
                max_tokens=2000
            )
            timetable = response.choices[0].message.content.strip()
        
        # Budget Generation
        with st.spinner("Generating Budget Estimates..."):
            budget_prompt = f"""
            The event will have {participants} participants.

            No heading needed.

            Include detailed budget items such as:
            - Venue (based on the location: '{event_location}')
            - Catering (based on participants and location)
            - Prizes (for winners)
            - Marketing (targeted based on the event location)
            - Equipment, Transportation (location-dependent)
            - Media Coverage
            - Speaker Fees (if location-specific)
            - Swag
            - Miscellaneous Expenses

            Ensure that the currency is appropriate for the event location ('{event_location}'). 
            Columns should include 'Budget Item', 'Estimated Cost (appropriate currency)' and 'Description'.

            Make sure all cells are filled, and do not use 'N/A'. At the end, provide the total estimated cost in this specific format:
            **Total Estimated Cost: [appropriate currency][Total Estimated Cost]** (Total Estimated Cost cannot be in the table)
            This should be clearly emphasized, making it easy to identify.

            This budget provides a comprehensive estimate for hosting {event_name} at {event_location}, ensuring all essential areas are considered.
            """
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": budget_prompt}],
                max_tokens=2000
            )
            budget_estimates = response.choices[0].message.content.strip()

            # Parse the budget estimates response
            budget_lines = budget_estimates.split('\n')
            budget_items = []
            budget_costs = []
            for line in budget_lines:
                if line.strip() and not line.startswith("Total Estimated Cost"):
                    parts = re.split(r'\s*-\s*', line.strip())
                    if len(parts) == 3:  # Expecting 'Budget Item - Estimated Cost - Description'
                        budget_items.append(parts[0])
                        budget_costs.append(float(re.sub(r'[^0-9.]', '', parts[1])))  # Extract the cost

            # Create DataFrame for the budget
            budget_df = pd.DataFrame({"Budget Item": budget_items, "Cost": budget_costs})
            
            # Generate the chart
            chart = alt.Chart(budget_df).mark_arc().encode(
                theta=alt.Theta(field="Cost", type="quantitative"),
                color=alt.Color(field="Budget Item", type="nominal"),
                tooltip=["Budget Item", "Cost"]
            )
        
        # Marketing & Promotion Suggestions
        with st.spinner("Generating Marketing & Promotion Suggestions..."):
            marketing_prompt = f"""
            Provide a list of marketing and promotion strategies for a hackathon named '{event_name}' with the theme '{event_theme}', happening in '{event_location}'.

            Include strategies for:
            - Social media marketing targeted to the region around '{event_location}'
            - Email campaigns and partnerships with local organizations in '{event_location}'
            - Physical and online marketing approaches (based on the event format: {event_format})
            
            Be direct and allow filtering options based on budget and channel. Do not display conclusion.
            """
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": marketing_prompt}],
                max_tokens=2000
            )
            marketing_suggestions = response.choices[0].message.content.strip()

        # Advanced AI Capabilities
        with st.spinner("Generating Speaker & Sponsor Suggestions..."):
            advanced_prompt = f"""
            Generate a list of potential speakers and sponsors for a hackathon named '{event_name}' with the theme '{event_theme}', happening in '{event_location}'.
            - Include names, organizations, and brief descriptions of why they would be a good fit.
            - Prioritize local speakers and sponsors based in or near '{event_location}'.
            Be direct. Allow filtering by industry or expertise. Do not display conclusion.
            """
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": advanced_prompt}],
                max_tokens=2000
            )
            advanced_suggestions = response.choices[0].message.content.strip()

        # Display Schedule, Budget, Marketing, and Advanced Suggestions in Tabs
        st.header("Event Planning")

        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Schedule", "Budget Estimates", "Marketing & Promotion", "Speakers & Sponsors"])

        # Schedule Tab
        with tab1:
            st.write(timetable)

        # Budget Tab
        with tab2:
            st.markdown(f"### Budget Estimates for {event_name}", unsafe_allow_html=True)
            st.write(budget_estimates)

        # Marketing & Promotion Tab
        with tab3:
            st.write(marketing_suggestions)

        # Speakers & Sponsors Tab
        with tab4:
            st.write(advanced_suggestions)
