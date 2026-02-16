### A. The Executive Summary
**Summary**
The snack market is filled with unhealthy snacks, with 'chocolates and candy' and 'cookies and biscuits' making up the largest category. Nuts and seeds have a high percentage of healthy products even thought they do not dominate the overall market. There is a lot of market opportunity in the 'chocolates and candy' and 'cookies and biscuits' categories, which are currently saturated eith high sugar low protein products. It will be a good category to produce more healthy snacks.

### B. Project Links
* **Link to Notebook:** [Notebook](https://colab.research.google.com/drive/1JwVEK_1ieml2wj3A1Ly9yV5G2LO7ftJ-?usp=sharing)
* **Link to Dashboard:** [Dashboard](https://the-market-gap-analysis-bfpcl4dcy39vhgzvrehvht.streamlit.app/)
* **Link to Presentation:** [Presentation](https://github.com/brighthann/The-Market-Gap-Analysis/blob/eb858a4f4ae81a190966cbc6e59fe572a771188c/The%20sugar_trap_market_analysis_presentation.pdf)

### C. Technical Explanation
**Data Cleaning**
The dataset was scanned systematically, and only the columns relevant to the analysis objectives were retained. this is a method which is analogous to the searching algorithm. filters were used to isolate records which met the stated criteria. this approach created a controlled dataset where only the targeted features of the dataset are present and, incomplete and invalid records are removed.
The next step involved converting the now workable data into a format that can easitly be handled. Eg. numeric columns are force converted to float type for better sorting. some of them contained text which made them unrecognizable, meaning they could not be used because they are not standalone numbers. these after failing the conversion, become NaN instead of raising an error. In short, the ral numbers hiding in the messy data are found and everything else is removed, so that calculations work properply.
  
**"Candidate's Choice"**
Finding brands with the highest percentage of healthy products involved using the health standard which was already defined in a previous story. This category makes use of high protein low salt products. the same data cleaning and filtering procedure that was used earlier was implemented. brands with multiple name entries were filtered - the first name is assumed to be the parent name and subsequent names are considered as sub brands. Similar names with difference in capitalization are considered the same brand and then standardized to title case. the cleaning procedure is implemented once for each row in the brands column. Brand aggregation is implemented afterwards - how many products does each brand have in total, and how many of those products are considered healthy; after that it is turned to a percentage. brands with few number of products are ignored. all rows that share the same brand name are grouped together. Aggregation functions are applied to each group such that, the count on the product name gives the total number of products that are high protein low sugar products. Unknown brands are excluded before grouping. Finally they are sorted from the highest health percentage to the lowest.


# Project Brief: The "Sugar Trap" Market Gap Analysis

**Client:** Helix CPG Partners (Strategic Food & Beverage Consultancy)  
**Deliverable:** Interactive Dashboard, Code Notebook & Insight Presentation

---

## 1. Business Context
**Helix CPG Partners** advises major food manufacturers on new product development. Our newest client, a global snack manufacturer, wants to launch a "Healthy Snacking" line. They believe the market is oversaturated with sugary treats, but they lack the data to prove where the specific gaps are.

They have hired us to answer one question: **"Where is the 'Blue Ocean' in the snack aisle?"**

Specifically, they are looking for product categories that are currently under-served—areas where consumer demand for health (e.g., High Protein, High Fiber) is not being met by current product offerings (which are mostly High Sugar, High Fat).

## 2. The Data
You will use the **Open Food Facts** dataset, a free, open, and massive database of food products from around the world.

* **Source:** [Open Food Facts Data](https://world.openfoodfacts.org/data)
* **Format:** CSV (Comma Separated Values)
* **Warning:** The full dataset is massive (over 3GB). You are **not** expected to process the entire file. You should filter the data early or work with a manageable subset (e.g., the first 500,000 rows or specific categories).

## 3. Tooling Requirements
You have the flexibility to choose your development environment:

* **Option A (Recommended):** Use a cloud-hosted notebook like **Google Colab**, or **Deepnote**, etc.
* **Option B:** Use a local **Jupyter Notebook** or **VS Code**.
    * *Condition:* If you choose this, you must ensure your code is reproducible. Do not reference local file paths (e.g., `C:/Downloads/...`). Assume the dataset is in the same folder as your notebook.
* **Dashboarding:** The final output must be a **publicly accessible link** (e.g., Tableau Public, Google Looker Studio, Streamlit Cloud, or PowerBI Web).

---

## 4. User Stories & Acceptance Criteria

### Story 1: Data Ingestion & "The Clean Up"
**As a** Strategy Director,  
**I want** a clean dataset that removes products with erroneous nutritional information,  
**So that** my analysis is not skewed by bad data entry.

* **Acceptance Criteria:**
    * Handle missing values: Decide what to do with rows that have `null` or empty `sugars_100g`, `proteins_100g`, or `product_name`.
    * Handle outliers: Filter out biologically impossible values.
    * **Deliverable:** A cleaned Pandas DataFrame or SQL table export.

### Story 2: The Category Wrangler
**As a** Product Manager,  
**I want** to group products into readable high-level categories,  
**So that** I don't have to look at 10,000 unique, messy tags like `en:chocolate-chip-cookies-with-nuts`.

* **Acceptance Criteria:**
    * The `categories_tags` column is a comma-separated string (e.g., `en:snacks, en:sweet-snacks, en:biscuits`). You must parse this string.
    * Create a logic to assign a "Primary Category" to each product based on keywords.
    * Create at least 5 distinct high-level buckets.

### Story 3: The "Nutrient Matrix" Visualization
**As a** Marketing Lead,  
**I want** to see a Scatter Plot comparing Sugar (X-axis) vs. Protein (Y-axis) for different categories,  
**So that** I can visually spot where the products are clustered.

* **Acceptance Criteria:**
    * Create a dashboard (PowerBI, Tableau, Streamlit, or Python-based charts) displaying this relationship.
    * Allow the user to filter the chart by the "High Level Categories" you created in Story 2.
    * **Key Visual:** Identify the "Empty Quadrant" (e.g., High Protein + Low Sugar).

### Story 4: The Recommendation
**As a** Client,  
**I want** a clear text recommendation on what product we should build,  
**So that** I can take this to the R&D team.

* **Acceptance Criteria:**
    * On the dashboard, include a "Key Insight" box.
    * Complete this sentence: *"Based on the data, the biggest market opportunity is in [Category Name], specifically targeting products with [X]g of protein and less than [Y]g of sugar."*

---

## 5. Bonus User Story: The "Hidden Gem"
**As a** Health Conscious Consumer,  
**I want** to know which specific ingredients are driving the high protein content in the "good" products,  
**So that** I can replicate this in our new recipe.

* **Acceptance Criteria:**
    * Analyze the `ingredients_text` column for products in your "High Protein" cluster.
    * Extract and list the Top 3 most common protein sources (e.g., "Whey", "Peanuts", "Soy").

---

## 6. The "Candidate's Choice" Challenge
**As a** Creative Analyst,  
**I want** to add one additional feature or analysis to this project that I believe provides massive value,  
**So that** I can show off my business acumen.

* **Instructions:**
    * Add one more chart, filter, or metric that wasn't asked for.
    * Explain **why** you added it.
    * **There is no wrong answer, but you must justify your choice.**

---

## 7. Submission Guidelines
Please edit this `README.md` file in your forked repository to include the following three sections at the top:

### A. The Executive Summary
* A 3-5 sentence summary of your findings.

### B. Project Links
* **Link to Notebook:** (e.g., Google Colab, etc.). *Ensure sharing permissions are set to "Anyone with the link can view".*
* **Link to Dashboard:** (e.g., Tableau Public / Power BI Web, etc.).
* **Link to Presentation:** A link to a short slide deck (PDF, PPT) AND (Optional) a 2-minute video walkthrough (YouTube) explaining your results.

### C. Technical Explanation
* Briefly explain how you handled the "Data Cleaning".
* Explain your "Candidate's Choice" addition.

**Important Note on Code Submission:**
* Upload your `.ipynb` notebook file to the repo.
* **Crucial:** Also upload an **HTML or PDF export** of your notebook so we can see your charts even if GitHub fails to render the notebook code.
* Once you are ready, please fill out the [Official Submission Form Here](https://forms.office.com/e/heitZ9PP7y) with your links

---

## 🛑 CRITICAL: Pre-Submission Checklist

**Before you submit your form, you MUST complete this checklist.**

> ⚠️ **WARNING:** If you miss any of these items, your submission will be flagged as "Incomplete" and you will **NOT** be invited to an interview. 
>
> **We do not accept "permission error" excuses. Test your links in Incognito Mode.**

### 1. Repository & Code Checks
- [ ✅ ] **My GitHub Repo is Public.** (Open the link in a Private/Incognito window to verify).
- [ ✅ ] **I have uploaded the `.ipynb` notebook file.**
- [ ✅ ] **I have ALSO uploaded an HTML or PDF export** of the notebook.
- [ ✅ ] **I have NOT uploaded the massive raw dataset.** (Use `.gitignore` or just don't commit the CSV).
- [ ✅ ] **My code uses Relative Paths.** 

### 2. Deliverable Checks
- [ ✅ ] **My Dashboard link is publicly accessible.** (No login required).
- [ ✅ ] **My Presentation link is publicly accessible.** (Permissions set to "Anyone with the link can view").
- [ ✅ ] **I have updated this `README.md` file** with my Executive Summary and technical notes.

### 3. Completeness
- [✅ ] I have completed **User Stories 1-4**.
- [✅ ] I have completed the **"Candidate's Choice"** challenge and explained it in the README.

**✅ Only when you have checked every box above, proceed to the submission form.**

---
