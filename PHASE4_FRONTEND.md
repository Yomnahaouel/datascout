# PHASE 4: Frontend UI Rebuild

## Task
Rebuild the frontend with a modern, beautiful UI using React, TypeScript, and Tailwind CSS.

## Pages to Create (5 total)

### 1. SearchPage (Route: /)
- Large centered hero section with DataScout logo
- Big search bar with search icon
- Popular tags below search (Finance, Fraud, Clients, Risk)
- 4 KPI stat cards (total datasets, total rows, avg quality, domains)
- Recently added datasets section with compact cards

### 2. BrowsePage (Route: /browse)
- Top search bar (smaller)
- Left sidebar with filters:
  - Domain checkboxes (Finance, Risk, Marketing, HR, Operations)
  - Quality score slider (0-100)
  - Format checkboxes (CSV, Excel, JSON)
  - PII radio buttons (All, Contains PII, No PII)
- Main area with dataset cards grid
- Pagination at bottom

### 3. DatasetProfilePage (Route: /datasets/:id)
- Back to Browse link
- Dataset header with name, description, tags, actions (View Dashboard, Download, Delete)
- 4 KPI cards (rows, columns, size, quality)
- Quality breakdown with 5 progress bars (Completeness, Consistency, Uniqueness, Validity, Timeliness)
- Column profile table (sortable)
- Data preview table (first 50 rows)

### 4. DashboardPage (Route: /datasets/:id/dashboard)
- Back to Profile link
- Dataset name
- 4 KPI cards
- Auto-generated charts in 2-column grid:
  - Histogram for numeric columns
  - Pie chart for categorical columns
  - Box plot for numeric columns
  - Heatmap for correlation matrix
  - Missing values horizontal bar chart

### 5. UploadModal
- Modal overlay
- Drag and drop zone
- Browse files button
- Optional name and description fields
- Progress steps (Uploading, Validating, Profiling, Detecting PII, Quality scoring, Indexing, Dashboard)
- Success state with quality score and links

## Components to Create

### Common Components
- Navbar.tsx - Logo, nav tabs (Search, Browse), Upload button, Settings
- SearchBar.tsx - Large and small variants
- KPICard.tsx - Big number with label
- QualityBadge.tsx - Color coded (green 80+, yellow 60-79, red <60)
- TagBadge.tsx - Domain tags (blue), PII warning (red)
- LoadingSpinner.tsx
- SkeletonCard.tsx

### Dataset Components
- DatasetCard.tsx - Compact card for home page
- DatasetCardExpanded.tsx - Larger card with description for browse
- DatasetHeader.tsx - Name, tags, actions
- QualityBreakdown.tsx - 5 progress bars
- ColumnProfileTable.tsx - Sortable table
- DataPreviewTable.tsx - Horizontally scrollable

### Chart Components (use Recharts)
- HistogramChart.tsx
- PieChartComponent.tsx
- BoxPlotChart.tsx
- HeatmapChart.tsx
- MissingValuesMap.tsx

### Filter Components
- FilterSidebar.tsx
- DomainFilter.tsx
- QualitySlider.tsx
- FormatFilter.tsx
- PIIFilter.tsx

### Upload Components
- UploadModal.tsx
- DropZone.tsx
- ProgressSteps.tsx
- SuccessSummary.tsx

## Design System

### Colors
- Primary: #3B82F6 (Blue)
- Secondary: #10B981 (Green)
- Warning: #F59E0B (Yellow)
- Danger: #EF4444 (Red)
- Background: #F9FAFB (Light gray)
- Card: #FFFFFF (White)
- Text Primary: #111827
- Text Secondary: #6B7280
- Border: #E5E7EB

### Typography
- Font: Inter (or system font)
- H1: text-3xl font-bold
- H2: text-2xl font-bold
- H3: text-xl font-bold
- Body: text-base
- Small: text-sm

### Spacing
- Card padding: p-4 or p-6
- Section gap: space-y-6
- Grid gap: gap-4 or gap-6

## API Integration
Connect to these endpoints:
- GET /api/v1/datasets - List datasets
- GET /api/v1/datasets/:id - Get dataset details
- GET /api/v1/datasets/:id/profile - Get column profiles
- GET /api/v1/datasets/:id/quality - Get quality scores
- GET /api/v1/datasets/:id/dashboard - Get dashboard config
- GET /api/v1/datasets/:id/preview - Get data preview
- POST /api/v1/datasets/upload - Upload file
- GET /api/v1/search?q= - Semantic search

## Requirements
- Use React Router for navigation
- Use Tailwind CSS for styling
- Use Recharts for charts
- Make it responsive (mobile, tablet, desktop)
- Add loading and error states
- Make it beautiful and professional!
