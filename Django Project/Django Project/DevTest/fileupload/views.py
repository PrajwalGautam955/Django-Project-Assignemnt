import pandas as pd
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

def upload_file(request):
    if request.method == 'POST':
        # Check if 'file' is in request.FILES
        if 'file' not in request.FILES:
            return HttpResponse("No file uploaded", status=400)
        
        file = request.FILES['file']
        
        try:
            # Load the Excel file
            df = pd.read_excel(file)
            
            # Verify if required columns are present
            required_columns = ['Cust State', 'Cust Pin', 'DPD']
            if not all(col in df.columns for col in required_columns):
                return HttpResponse("Uploaded file must contain 'Cust State', 'Cust Pin', and 'DPD' columns.", status=400)
            
            # Select only the necessary columns and rename them
            df = df[required_columns]
            df.columns = ['Cust_State', 'Cust_Pin', 'DPD']
            
            # Group by Cust_State and Cust_Pin, and count the occurrences of each Cust_Pin
            df_grouped = df.groupby(['Cust_State', 'Cust_Pin']).size().reset_index(name='DPD')
            
            # Filter rows where DPD (count of duplicates) is more than 1
            duplicate_rows = df_grouped[df_grouped['DPD'] > 1]
            
            # Convert DataFrame to list of dictionaries for template rendering
            summary = duplicate_rows.to_dict(orient='records')
            
            # Prepare email body with the summary data
            email_body = "\n".join([f"{row['Cust_State']}, {row['Cust_Pin']}, {row['DPD']}" for row in summary])
            send_mail(
                subject='Python Assignment -Prajwal Gautam',
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['tech@themedius.ai'],
                fail_silently=False,
            )
            
            return render(request, 'summary.html', {'summary': summary})
        
        except Exception as e:
            return HttpResponse(f"An error occurred while processing the file: {e}", status=500)
        
    return render(request, 'upload.html')
