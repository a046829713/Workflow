function Open_attachmentarea() {
    $('.attachmentarea').show()
}
function close_window() {
    $('.attachmentarea').hide()
}

function handleFileUpload(index, if_only_upload_and_this_is_id = null) {
    const fileInput = document.getElementById('fileInput' + index);
    const file = fileInput.files[0];

    if (!file) {
        alert('請選擇一個文件');
        return;
    }

    // 通常會有一個百分比進度框
    var traget_id = '#percent_to_upload' + index;

    var location_file_neme = "attachment" + index;

    uploadFileInChunks(file, traget_id, location_file_neme, if_only_upload_and_this_is_id).then(result => {
        // 看看有沒有接收到form表單的ID
        if (result) {
            $('#percent_to_upload' + index).text("上傳成功");
            $('#percent_to_upload' + index).addClass("text-success");
            $('#percent_to_upload' + index).removeClass("text-danger");
        }

        // 將預先準備好的表單ID回傳
        if (!if_only_upload_and_this_is_id) {
            $('input[name="form_id_Per"]').val(result.form_id_Per);
        }


    }).catch(error => {
        console.error('上傳過程中出錯:', error);
        alert('上傳檔案失敗，請洽資訊課');
    });
}


// 生成亂碼的函數
function generateRandomString(length) {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '_';
    const charactersLength = characters.length;
    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

function uploadFileInChunks(file, traget_id, location_file_neme, if_only_upload_and_this_is_id = null) {
    // file : 要上傳之檔案
    // traget_id : 頁面上需要有百分比顯示條(span)

    const chunkSize = 10485760; // 每塊大小為10MB
    const totalChunks = Math.ceil(file.size / chunkSize); // 計算總塊數
    let currentChunk = 0; // 當前塊的索引

    const randomString = generateRandomString(7); // 生成7位的亂碼
    const modifiedFileName = file.name.split('.').map((part, index, array) => index === array.length - 1 ? randomString + '.' + part : part).join('');

    return new Promise((resolve, reject) => {
        // 定義上傳下一塊文件的函數
        function uploadNextChunk() {
            const start = currentChunk * chunkSize; // 當前塊的開始位置
            const end = Math.min(start + chunkSize, file.size); // 當前塊的結束位置
            const chunk = file.slice(start, end); // 提取當前塊

            // 創建一個 FormData 對象來包含這塊文件和相關信息
            const formData = new FormData();
            formData.append('file', chunk); // 添加文件塊
            formData.append('chunkNumber', currentChunk); // 添加當前塊的索引
            formData.append('totalChunks', totalChunks); // 添加總塊數
            formData.append('filename', modifiedFileName); // 將亂碼製作過後的file傳出
            formData.append('location_file_neme', location_file_neme); // 文件位址控管附件

            // 獲取表單中的所有隱藏元素
            const hiddenInputs = document.querySelectorAll('Form input[type="hidden"]');

            // 將每個隱藏元素的 name 和 value 添加到 FormData 對象中
            hiddenInputs.forEach(input => {
                formData.append(input.name, input.value);
            });


            // 假設是沒有表單模型的情況下要去上傳的話要將id傳出去
            if ((if_only_upload_and_this_is_id)) {
                console.log("上傳進入")
                formData.append("form_id_Per", if_only_upload_and_this_is_id);
            }

            // 使用 fetch API 發送 POST 請求上傳當前文件塊
            fetch('/upload/', {
                method: 'POST',
                body: formData,
            }).then(response => response.json()) // 將響應解析為 JSON
                .then(data => {
                    // 如果還有剩餘的文件塊，遞增當前塊的索引並上傳下一塊
                    if (currentChunk < totalChunks - 1) {
                        // 狀態更新
                        $(traget_id).text(`上傳進度:${Math.floor(currentChunk / totalChunks * 100)}%`);
                        $(traget_id).addClass("text-danger");;
                        currentChunk++;
                        uploadNextChunk();
                    } else {
                        // 所有文件塊上傳完成
                        resolve(data);
                    }
                })
                .catch(error => {
                    // 處理上傳過程中的錯誤
                    console.error('Error uploading chunk:', error);
                    reject(error);
                });
        }

        // 開始上傳第一塊文件
        uploadNextChunk();
    });
}