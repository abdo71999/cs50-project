USER
  ↓
uploads CSV
  ↓
system reads CSV
  ↓
system extracts column names
  ↓
user selects X and Y
  ↓
system validates selected X and Y
   ├── invalid → show error → user corrects selection/data
   │
   └── valid
        ↓
perform linear regression
        ↓
calculate:
b₁, b₀, R², RMSE,
predicted Y, residuals
        ↓
create visualizations:
scatter + fitted line
residual plot
        ↓
display numerical + visual results
        ↓
USER interprets results