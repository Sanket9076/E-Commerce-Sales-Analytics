import sqlite3
import run_queries as rq

def main():
    conn = sqlite3.connect("SQL/ecommerce_analytics.db")
    cursor = conn.cursor()
    
    for i in range(1, 11):
        title, query = rq.QUERIES[i]
        print(f"\n======================================================================")
        print(f" Query {i}: {title}")
        print(f"======================================================================")
        
        cursor.execute(query)
        headers = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        formatted_rows = []
        for row in rows:
            formatted_row = []
            for val in row:
                if isinstance(val, float):
                    formatted_row.append(f"{val:,.2f}")
                elif isinstance(val, int) and val > 10000:
                    formatted_row.append(f"{val:,}")
                else:
                    formatted_row.append(val)
            formatted_rows.append(formatted_row)
            
        rq.print_table(headers, formatted_rows)
        print(f"Returned {len(rows)} row(s).")
        
    conn.close()

if __name__ == "__main__":
    main()
