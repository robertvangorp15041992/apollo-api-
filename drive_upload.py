def upload_to_drive(filename):
    credentials_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])

    creds = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=['https://www.googleapis.com/auth/drive']
    )

    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': filename,
        'parents': ['1vIZc_2DqNgwZm3dFFW5GpPvm_zZzgaMo'],  # 👈 your folder ID
        'mimeType': 'application/vnd.google-apps.spreadsheet'  # Optional
    }

    media = MediaFileUpload(filename, mimetype='text/csv')

    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = uploaded.get('id')

    # Make file shareable by anyone with link
    service.permissions().create(
        fileId=file_id,
        body={
            'role': 'reader',
            'type': 'anyone',
        }
    ).execute()

    shareable_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    return shareable_link
