import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Company.models import Form, Attachment
from workFlow.DataTransformer import querydict_to_dict, GetFormID
from workFlow.Appsettings import SAVE_ATTACHMENT_PATH
def check_form_name(request) -> str:
    # 假設是審核的時候沒有傳進來 自己用ID搜尋
    form_name = request.POST.get('form_name', 'form_name')
    if form_name =='form_name':            
        form_name = Form.objects.get(form_id = request.POST.get('form_id_Per', 'form_id_Per')).form_name
    return form_name
    
@csrf_exempt
def upload_view(request):
    if request.method == 'POST':        
        chunk = request.FILES['file']
        chunk_number = int(request.POST['chunkNumber'])
        total_chunks = int(request.POST['totalChunks'])
        
        filename = request.POST.get('filename', 'uploaded_file')
        form_name = check_form_name(request)        
        
        # 取得位址檢查是否存在
        location_file_neme = request.POST.get('location_file_neme', 'location_file_neme')

        upload_dir = os.path.join(settings.MEDIA_ROOT, SAVE_ATTACHMENT_PATH[form_name])        
        
        os.makedirs(upload_dir, exist_ok=True)        
        file_path = os.path.join(upload_dir, filename)

        with open(file_path, 'ab') as f:
            f.write(chunk.read())

        if chunk_number == total_chunks - 1:
            # 檔案全部上傳之後在保存
            post_data = querydict_to_dict(request.POST)
            form_id_Per = post_data.pop('form_id_Per', '')        
            
            # 先判斷之前是否已經有資料
            if form_id_Per:
                form = Form.objects.get(form_id = form_id_Per)
            else:
                form = Form()
                form.form_id = GetFormID(post_data.pop('form_id', None))
                form.form_name = post_data.pop('form_name', '')
                form.applicant = post_data.pop('applicant', '')
                form.data = {}
                form.version_number = post_data.pop('version_number', '')
                form.parents_form_id = post_data.pop('parents_form_id', '')
                form.save()
              
            # 文件已全部上傳完畢，創建並保存附件
            # # 附件時要對應位置上傳            

            
            # 如果有同名的附件，删除它
            existing_attachments = Attachment.objects.filter(name=location_file_neme, form_id=form.form_id)
            for attachment in existing_attachments:
                attachment.file.delete()
                attachment.delete()
            
            attachment = Attachment(
                name=location_file_neme,
                form_name=form.form_name,
                form_id=form.form_id,
                file=os.path.join(SAVE_ATTACHMENT_PATH[form_name], filename)
            )
            
            attachment.save()
            form.attachments.add(attachment)
            form.save()
            print("保存測試")
            return JsonResponse({'status': 'completed',"form_id_Per":form.form_id})
        else:
            return JsonResponse({'status': 'chunk_received'})

    return JsonResponse({'status': 'error'}, status=400)



            





