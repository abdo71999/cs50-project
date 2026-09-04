## Component 1: Data Handling
Responsibilities: 
 1) Read the data from CSV + read column names
CSV file
   ↓
read file
   ↓
understand rows/columns
   ↓
provide column names + data

 2) Select X /Y then check if there are null values in those columns

## Component 2: Analysis
Responsibilities: 
 1) Perform regression 
 2) calculate metrics


## Component 3: Visualization
Responsibilities: 
 1) Fit Visualization 
 2) Residual Visualization
 3) show graphs

## Component 4: UI
 1) upload button
 2) sign in 
 3) previous results 
 4) not sure what else or this is too much 


                 PHYSICS DATA LAB — V0

                       USER
                        │
                        ▼
               ┌────────────────┐
               │ User Interface │
               └───────┬────────┘
                       │ CSV
                       ▼
               ┌────────────────┐
               │ Data Handling  │
               │                │
               │ • read CSV     │
               │ • columns      │
               │ • select X/Y   │
               │ • validate     │
               └───────┬────────┘
                       │ valid X,Y
                       ▼
               ┌────────────────┐
               │    Analysis    │
               │                │
               │ • regression   │
               │ • b₀, b₁       │
               │ • R²           │
               │ • RMSE         │
               │ • predictions  │
               │ • residuals    │
               └───────┬────────┘
                       │
              ┌────────┴─────────┐
              ▼                  ▼
       numerical results    visualization
              │                  │
              └────────┬─────────┘
                       ▼
               ┌────────────────┐
               │ User Interface │
               │ displays result│
               └────────────────┘