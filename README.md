# Sales Performance Dashboard

This project is an interactive dashboard designed to track and visualise the performance of a sales team for a fictional AI tech company. It demonstrates skills in **data synthesis, preprocessing, and dashboard development** using Python and popular data science libraries(Streamlit, Pyplot etc).

---

## Features

- **Synthetic Data Generation**: Automatically creates realistic sales data for demonstration purposes.  
- **Data Preprocessing**: Cleans and prepares the dataset for analysis and visualization.  
- **Interactive Dashboard**: A centralized interface for exploring sales performance metrics.  
- **Modular Design**: Each step (data generation, preprocessing, visualization) is separated for clarity and reusability.

## 📂 Project Structure

```bash
.
├── script.py            # Generates synthetic sales data
├── preprocessing.ipynb  # Jupyter Notebook for data cleaning and preparation
├── app2.py              # Main entry point for the dashboard
├── ui_components        # Folder containing logic for all the tabs i
├── requirements.txt     # List of dependencies
└── README.md            # Project documentation
```
## Installation

1. Clone this repository
```bash
git clone https://github.com/Pako-Mampane/Dashboard.git
cd Dashboard
```

2. Create and activate a virtual environment
  ```bash
  python -m venv venv
  source venv/bin/activate   # On macOS/Linux
  venv\Scripts\activate      # On Windows
```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Generate the synthetic data
   ```bash
   python script.py
   ```
2. Preprocess the data
   Open and run the Jupyter notebook: Preprocessing.ipynb
   
4. Launch the dashboard
   ```bash
   streamlit run app2.py
   ```
   
## Skills Demonstrated

- Python scripting for data generation
- Data cleaning & transformation in Jupyter notebooks
- Dashboard development and visualization
- Project structuring & dependency management

## License
This project is for educational and portfolio purposes. Feel free to use or adapt it with attribution.

## Author
Developed by Pako Mampane

LinkedIn: https://www.linkedin.com/in/pako-mampane-a2873b254/
