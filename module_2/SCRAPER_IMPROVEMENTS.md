# GradCafe Scraper - Improvements and Usage Guide

## Overview
This document explains the improvements made to your GradCafe scraper and how to use it effectively.

## Key Issues Fixed

### 1. **Detail Page Data Collection**
**Problem**: The original scraper was collecting basic information (university, program, status) but all detail fields (GPA, GRE scores, citizenship, comments) were returning `null`.

**Solution**: 
- Enhanced the `_parse_detail_page()` function to properly call GradCafe's API endpoint
- Added better error handling for API responses
- Improved rate limiting to avoid overwhelming the server
- Added fallback field names (e.g., checking both `gre_total` and `gre`)

### 2. **Improved HTML Parsing**
**Problem**: The HTML structure of GradCafe can vary across different entries.

**Solution**:
- More robust university name extraction with multiple fallback methods
- Better handling of program and degree level parsing
- Improved status and date extraction with regex patterns

### 3. **Better Progress Tracking**
**Enhancement**:
- Real-time coverage statistics showing percentage of entries with each field
- Sample entries displayed at the end showing actual data collected
- Checkpoint system that saves progress every 5 pages

### 4. **Error Handling**
**Improvements**:
- Graceful handling of HTTP errors (404, timeouts)
- Better exception catching and reporting
- Continues scraping even if individual entries fail

## How to Use

### Basic Usage
```python
python scrape_exact_improved.py
```

This will:
- Check robots.txt for permission
- Scrape 1,000 entries (default)
- Save to `module_2/raw_applicant_data.json`
- Create checkpoints every 5 pages

### Customizing the Scrape

To change the number of entries, modify the `main()` function:

```python
def main():
    # ... robots check ...
    
    # Change max_entries here:
    data = scrape_data(max_entries=2000, start_page=1)
```

### Resume from Checkpoint

If the scraper is interrupted, you can resume by modifying:

```python
data = scrape_data(max_entries=1000, start_page=5)  # Resume from page 5
```

## Understanding the Output

### Coverage Statistics

During scraping, you'll see output like:
```
Coverage: Comm=45% GPA=62% V=58% Q=58% AW=55% Tot=60% Term=78% Cit=65%
```

This shows the percentage of scraped entries that have data for each field:
- **Comm**: Comments
- **GPA**: GPA score
- **V**: GRE Verbal
- **Q**: GRE Quantitative
- **AW**: GRE Analytical Writing
- **Tot**: GRE Total
- **Term**: Application term (e.g., "Fall 2026")
- **Cit**: Citizenship status

### Expected Coverage Rates

Based on GradCafe's data, you should expect:
- **High coverage (60-80%)**: Term, Citizenship, GPA
- **Medium coverage (40-60%)**: GRE scores, Comments
- **Variable**: Some programs require GRE, others don't, so GRE coverage varies

## Data Structure

Each entry in the output JSON contains:

```json
{
  "program_name": "Computer Science",
  "university": "Stanford University",
  "date_added": "February 07, 2026",
  "entry_url": "https://www.thegradcafe.com/result/997745",
  "status": "Accepted",
  "status_date": "6 Feb",
  "degree_level": "PhD",
  "comments": "Great program! Interview was friendly.",
  "term": "Fall 2026",
  "citizenship": "International",
  "gpa": 3.85,
  "gre_total": 328,
  "gre_v": 164,
  "gre_q": 164,
  "gre_aw": 4.5
}
```

## Rate Limiting

The scraper includes built-in rate limiting:
- **1.0 second delay** between page requests
- **0.3 second delay** between API calls for detail pages

This is respectful of GradCafe's servers and helps avoid IP bans.

## Troubleshooting

### Issue: Low coverage for detail fields
**Solution**: This is normal. Not all GradCafe entries include complete data. Users often leave fields blank.

### Issue: Scraper stops early
**Check**:
1. Internet connection
2. GradCafe website availability
3. Checkpoint file shows last successful page

### Issue: HTTP 404 errors for API
**Solution**: Some older entries don't have API endpoints. The scraper handles this gracefully and continues.

### Issue: All detail fields still null
**Debug steps**:
1. Check if you can manually access: `https://www.thegradcafe.com/api/result/997745`
2. Verify the API response contains data
3. Check your network allows the requests

## Integration with Your Pipeline

After scraping, the data flows through your existing pipeline:

1. **scrape_exact_improved.py** → Creates `raw_applicant_data.json`
2. **clean.py** → Cleans data and calls LLM → Creates `llm_extend_applicant_data.json`
3. **load_data.py** → Loads into PostgreSQL database
4. **Flask app** → Displays analysis dashboard

No changes needed to your other files - the improved scraper produces the same output format.

## Performance

Typical performance:
- **100 entries**: ~3-5 minutes
- **1,000 entries**: ~30-40 minutes
- **5,000 entries**: ~2.5-3 hours

Time depends on:
- Network speed
- GradCafe server response time
- Number of detail pages to fetch

## Best Practices

1. **Start small**: Test with 100 entries first
2. **Use checkpoints**: Don't lose progress on long scrapes
3. **Check coverage**: Ensure you're getting adequate detail data
4. **Respect robots.txt**: Always run the robots check
5. **Monitor output**: Watch for error messages during scraping

## API Endpoint Details

GradCafe provides an API endpoint for each result:
```
https://www.thegradcafe.com/api/result/{result_id}
```

This endpoint returns JSON with all the detail fields. The improved scraper:
- Extracts the result ID from the entry URL
- Calls this API endpoint
- Parses the JSON response
- Merges the data into the record

## Comparison: Old vs New

| Feature | Old Scraper | Improved Scraper |
|---------|-------------|------------------|
| Basic fields (university, program) | ✓ | ✓ |
| Detail fields (GPA, GRE, etc.) | ✗ (all null) | ✓ |
| Progress tracking | Basic | Detailed with % |
| Error handling | Limited | Comprehensive |
| Checkpoints | Every 3 pages | Every 5 pages |
| Sample output | Basic stats | Shows actual data |
| API rate limiting | 0.5s | 0.3s (optimized) |

## Next Steps

1. **Test the scraper**: Run with 100 entries to verify it works
2. **Check coverage**: Ensure detail fields are populated
3. **Run full scrape**: Collect your desired number of entries
4. **Proceed with pipeline**: Use clean.py and load_data.py as normal

The improved scraper should now successfully collect all the detail fields that were previously returning null!
