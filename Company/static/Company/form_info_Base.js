function close_window() {
    // 使模態框中的"x"按鈕能夠關閉模態框
    $('#BusinessCardRequestarea').css('display', 'none');
    $('#complaintarea').css('display', 'none');
    $('#ExternalProcessingarea').css('display', 'none');
    $('#DDBarea').css('display', 'none');
    $('#dataVerification').css('display', 'none');
    $('#DDBarea').css('display', 'none');
    $('#DrawingDependencyBookarea').css('display', 'none');
    $('.approval_opinionarea').css('display', 'none');
    $('.noteInput').val('');
    $("#Heavyworkorderarea").css("display", "none");
    $("#ExperimentalTestarea").css("display", "none");
};

function submitBusinessCardRequest(button) {
    // 隐藏模态框
    $("#BusinessCardRequestarea").css("display", "none");
    // 获取文字区域的值
    var releasedate = $('#id_releasedate').val();
    // 正确获取单选按钮的值
    var ifRecycle = $('input[name="ifRecycle"]:checked').val();

    if (!releasedate || !ifRecycle) {
        alert("請填寫所有必填欄位。");
        $("#BusinessCardRequestarea").css("display", "block");
        return; // 阻止函数继续执行
    }
    // 创建隐藏的输入字段并附加到表单
    $('<input>').attr({ type: 'hidden', name: 'releasedate', value: releasedate }).appendTo('form');
    $('<input>').attr({ type: 'hidden', name: 'ifRecycle', value: ifRecycle }).appendTo('form');

    // 模擬點擊先前儲存的按鈕以提交表單
    $(clickedButton).click();
};


function submitCAR(button) {
    // 隐藏模态框
    $("#DDBarea").css("display", "none");

    // 获取文字区域的值
    var complaint_reason = $('#complaint_reason').val();
    var temporary_plan = $('#temporary_plan').val();

    // 创建隐藏的输入字段并附加到表单
    $('<input>').attr({ type: 'hidden', name: 'complaint_reason', value: complaint_reason }).appendTo('form');
    $('<input>').attr({ type: 'hidden', name: 'temporary_plan', value: temporary_plan }).appendTo('form');


    // 模擬點擊先前儲存的按鈕以提交表單
    $(clickedButton).click();
};

function submitDDB(button) {
    // 隐藏模态框
    $("#DrawingDependencyBookarea").css("display", "none");
    // 获取文字区域的值
    var rdgroupSelect = $('#rdgroupSelect').val();
    // 创建隐藏的输入字段并附加到表单
    $('<input>').attr({ type: 'hidden', name: 'rdgroupSelect', value: rdgroupSelect }).appendTo('form');
    // 模擬點擊先前儲存的按鈕以提交表單
    $(clickedButton).click();
};


function submitQAR(button) {
    // 隐藏模态框
    $("#DDBarea").css("display", "none");

    // 获取所有选中的选项，并添加为隐藏的输入字段
    $(".select2-multiple").each(function () {
        $(this).find(":selected").each(function () {
            $('<input>').attr({
                type: 'hidden',
                name: 'endorsement_asigns', // 可以根据需要更改此名称
                value: $(this).val()
            }).appendTo('form'); // 确保这是你表单的正确选择器
        });
    });

    // 模擬點擊先前儲存的按鈕以提交表單
    $(clickedButton).click();
};

function submitdataVerification(button) {
    // 隐藏模态框
    $("#dataVerification").css("display", "none");

    // 获取文字区域的值
    var cause_analysis = $('#cause_analysis').val();
    var temporary_measures = $('#temporary_measures').val();
    var permanent_disposal_countermeasures = $('#permanent_disposal_countermeasures').val();

    // 创建隐藏的输入字段并附加到表单
    $('<input>').attr({ type: 'hidden', name: 'cause_analysis', value: cause_analysis }).appendTo('form');
    $('<input>').attr({ type: 'hidden', name: 'temporary_measures', value: temporary_measures }).appendTo('form');
    $('<input>').attr({ type: 'hidden', name: 'permanent_disposal_countermeasures', value: permanent_disposal_countermeasures }).appendTo('form');

    // 模擬點擊先前儲存的按鈕以提交表單
    $(clickedButton).click();
};



function submitComplaint(button) {
    // 用來跳出視窗讓客訴處理員可以填入相關的資料和處置 
    var complaintResolutionStatus = $('#IRCC').val();
    if (!complaintResolutionStatus) {
        alert("請確認已經寫入內部初步回覆")
    } else {
        $('<input>').attr({
            type: 'hidden',
            name: 'complaintResolutionStatus',
            value: complaintResolutionStatus
        }).appendTo('form');
    }
    // Hide the modal
    $("#complaintarea").css("display", "none");
    // 模擬點擊先前儲存的按鈕以提交表單
    $(clickedButton).click();
};


function submitResponeCustomer(button) {
    // 用來跳出視窗讓業務人員可以根據客訴處理員的處理資訊來回覆客人 
    var externalprocessing = $('#respone_customer').val();
    if (!externalprocessing) {
        alert("請確認已經填寫對外處理內容")
    } else {
        $('<input>').attr({
            type: 'hidden',
            name: 'externalprocessing',
            value: externalprocessing
        }).appendTo('form');
    }

    // Hide the modal
    $("#ExternalProcessingarea").css("display", "none");
    // 模擬點擊先前儲存的按鈕以提交表單
    $(clickedButton).click();
};


function submitExperimentalTest(button) {
    console.log("測試進入")
    // 用來跳出視窗可以讓生產部生計課人員 可以回覆完成日期
    var estimated_completion_date = $('#estimated_completion_date').val();
    if (!estimated_completion_date) {
        alert("請確認已經填寫預計完成日期")
    } else {
        $('<input>').attr({
            type: 'hidden',
            name: 'estimated_completion_date',
            value: estimated_completion_date
        }).appendTo('form');
    }

    // Hide the modal
    $("#ExperimentalTestarea").css("display", "none");
    // 模擬點擊先前儲存的按鈕以提交表單
    $(clickedButton).click();
};







function submitRWF() {
    // 用來跳出視窗讓生管課長可以選擇要預設完工的時間
    var estimated_completion_date = $('#id_estimated_completion_date').val();
    if (!estimated_completion_date) {
        alert("請確認已經選擇預計完工日期")
    } else {
        $('<input>').attr({
            type: 'hidden',
            name: 'estimated_completion_date',
            value: estimated_completion_date
        }).appendTo('form');
    }
    var approval_opinion = $('#Heavyworkorder_opinion').val();
    // 创建隐藏的输入字段并附加到表单
    var form = $(clickedButton).closest('form'); // 找到最接近的form元素
    $('<input>').attr({ type: 'hidden', name: 'approval_opinion', value: approval_opinion }).appendTo(form);

    // Hide the modal
    $("#Heavyworkorderarea").css("display", "none");

    // 模擬點擊先前儲存的按鈕以提交表單
    $(clickedButton).click();
};
function submitNote(button) {
    // 隐藏模态框
    $(".approval_opinionarea").css("display", "none");
    var approval_opinion = $(button).closest('.approval_opinion-content').find('.noteInput').val();
    // 创建隐藏的输入字段并附加到表单
    var form = $(clickedButton).closest('form'); // 找到最接近的form元素
    $('<input>').attr({ type: 'hidden', name: 'approval_opinion', value: approval_opinion }).appendTo(form);
    $(clickedButton).click();
};

// 當簽核完之後如果有特殊的需求就要撰寫以下的代碼
function handleClick(button) {
    if ($("#target_form_name").text() == '客訴紀錄單' && $(button).val() == '核准') {
        var form = $(button).closest('form'); // 找到最接近的form元素
        var inputExists = form.find('input[name="complaintResolutionStatus"]').length > 0; // 檢查input元素是否存在
        

        if (inputExists ) {
            // 如果存在名為"complaint_departments"的input元素，則執行相應的邏輯
            // 例如，你可以在這裡添加處理邏輯或返回特定值
            return true;
        } else {
            // 顯示模態框
            $("#complaintarea").css("display", "block");
            clickedButton = button; // 儲存點擊的按鈕
            return false;
        }
    } else if ($("#target_form_name").text() == '重工單' && $(button).val() == '確認') {
        var form = $(button).closest('form'); // 找到最接近的form元素
        var estimated_completion_date = form.find('input[name="estimated_completion_date"]').length > 0; // 檢查input元素是否存在

        if (estimated_completion_date) {
            return true;
        } else {
            // 顯示模態框
            $("#Heavyworkorderarea").css("display", "block");
            clickedButton = button; // 儲存點擊的按鈕
            return false;
        }

    } else if ($("#target_form_name").text() == '實驗測試申請單' && $(button).val() == '確認') {
        var form = $(button).closest('form'); // 找到最接近的form元素
        var estimated_completion_date = $("#estimated_completion_date").val()


        if (estimated_completion_date) {
            return true;
        } else {
            // 顯示模態框
            $("#ExperimentalTestarea").css("display", "block");
            clickedButton = button; // 儲存點擊的按鈕
            return false;
        }
    } else if ($("#target_form_name").text() == '名片申請單' && $(button).val() == '結案') {
        var form = $(button).closest('form'); // 找到最接近的form元素
        var inputExists = form.find('input[name="releasedate"]').length > 0; // 檢查input元素是否存在
        var inputifRecycle = form.find('input[name="ifRecycle"]').length > 0;

        if (inputExists & inputifRecycle) {
            // 如果存在名為"complaint_departments"的input元素，則執行相應的邏輯
            // 例如，你可以在這裡添加處理邏輯或返回特定值
            return true;
        } else {
            // 顯示模態框
            $("#BusinessCardRequestarea").css("display", "block");
            clickedButton = button; // 儲存點擊的按鈕
            return false;
        }
    } else if ($("#target_form_name").text() == '客訴紀錄單' && $(button).val() == '確認' && $('input[name="next_station"]').val() == '申請業務確認') {
        var form = $(button).closest('form'); // 找到最接近的form元素
        var inputExists = form.find('input[name="externalprocessing"]').length > 0; // 檢查input元素是否存在
        if (inputExists) {
            // 如果存在名為"complaint_departments"的input元素，則執行相應的邏輯
            // 例如，你可以在這裡添加處理邏輯或返回特定值
            return true;
        } else {
            // 顯示模態框
            $("#ExternalProcessingarea").css("display", "block");
            clickedButton = button; // 儲存點擊的按鈕
            return false;
        }

    } else if ($("#target_form_name").text() == '出圖依賴書' && $(button).val() == '確認' && $("#version").text() == 'B' && $("input[name='next_station']").val() == '資料準備完成') {
        // 上傳檔案和提交表單分開
        var form = $(button).closest('form'); // 找到最接近的form元素
        // 獲取所有 span 元素的集合
        const spanElements = document.querySelectorAll('[id^="percent_to_upload"]');
        var if_update_fie = false;

        // 遍歷每個 span 元素並取得其內容
        spanElements.forEach(span => {
            if (span.innerText == '上傳成功'){
                if_update_fie = true
            };
        });

        // 檢查input元素是否存在 因為會二次點擊所以要判斷
        if (if_update_fie) {
            return true;
        } else {
            alert("如果是第一次上傳檔案，務必將檔案上傳!")
            alert("如果是已經有上傳過檔案被駁回，務必重新上傳檔案(會將舊的檔案覆蓋)，例如:附件7會覆蓋附件7")

            // 顯示模態框
            $("#DDBarea").css("display", "block");
            clickedButton = button; // 儲存點擊的按鈕
            return false;
        }
    } else if ($("#target_form_name").text() == '出圖依賴書' && $(button).val() == '核准' && $("#version").text() == 'B' && $("input[name='next_station']").val() == '研發主管發案確認') {
        var form = $(button).closest('form'); // 找到最接近的form元素

        // 檢查input元素是否存在 因為會二次點擊所以要判斷
        var inputExists = form.find('input[name="rdgroupSelect"]').length > 0;
        if (inputExists) {
            // 如果存在名為"complaint_departments"的input元素，則執行相應的邏輯
            // 例如，你可以在這裡添加處理邏輯或返回特定值
            return true;
        } else {
            // 顯示模態框
            $("#DrawingDependencyBookarea").css("display", "block");
            clickedButton = button; // 儲存點擊的按鈕
            return false;
        }
    } else if ($("#target_form_name").text() == '出圖依賴書' && $(button).val() == '核准' && $("#version").text() == 'B' && $("input[name='next_station']").val() == '研發負責組別') {
        var form = $(button).closest('form'); // 找到最接近的form元素

        // 檢查input元素是否存在 因為會二次點擊所以要判斷
        var inputExists = form.find('input[name="rdgroupSelect"]').length > 0;
        if (inputExists) {
            // 如果存在名為"complaint_departments"的input元素，則執行相應的邏輯
            // 例如，你可以在這裡添加處理邏輯或返回特定值
            return true;
        } else {
            // 顯示模態框
            $("#DrawingDependencyBookarea").css("display", "block");
            clickedButton = button; // 儲存點擊的按鈕
            return false;
        }
    }
    else if ($("#target_form_name").text() == '品質異常單' && $(button).val() == '加簽') {
        var form = $(button).closest('form'); // 找到最接近的form元素

        // 檢查input元素是否存在 因為會二次點擊所以要判斷
        var inputExists = form.find('input[name="endorsement_asigns"]').length > 0;
        if (inputExists) {
            // 如果存在名為"complaint_departments"的input元素，則執行相應的邏輯
            // 例如，你可以在這裡添加處理邏輯或返回特定值
            return true;
        } else {
            // 顯示模態框
            $("#DDBarea").css("display", "block");
            clickedButton = button; // 儲存點擊的按鈕
            return false;
        }
    } else if ($("#target_form_name").text() == '品質異常單' && $(button).val() == '確認') {
        var form = $(button).closest('form'); // 找到最接近的form元素

        // 檢查input元素是否存在 因為會二次點擊所以要判斷
        var inputExists = form.find('input[name="cause_analysis"]').length > 0;
        if (inputExists) {
            // 如果存在名為"complaint_departments"的input元素，則執行相應的邏輯
            // 例如，你可以在這裡添加處理邏輯或返回特定值
            return true;
        } else {
            // 顯示模態框
            $("#dataVerification").css("display", "block");
            clickedButton = button; // 儲存點擊的按鈕
            return false;
        }
    } else if ($("#target_form_name").text() == '矯正預防措施處理單' && $(button).val() == '結案') {
        var form = $(button).closest('form'); // 找到最接近的form元素

        // 檢查input元素是否存在 因為會二次點擊所以要判斷
        var inputExists = form.find('input[name="complaint_reason"]').length > 0;
        if (inputExists) {
            // 如果存在名為"complaint_departments"的input元素，則執行相應的邏輯
            // 例如，你可以在這裡添加處理邏輯或返回特定值
            return true;
        } else {
            // 顯示模態框
            $("#DDBarea").css("display", "block");
            clickedButton = button; // 儲存點擊的按鈕
            return false;
        }
    } else if ($("#target_form_name").text() == '門禁權限申請單' && $(button).val() == '確認') {
        // return true;
        var form = $(button).closest('form'); // 找到最接近的form元素
        var inputExists = form.find('input[name="approval_opinion"]').length > 0; // 檢查input元素是否存在
        if (inputExists) {
            // 如果存在名為"complaint_departments"的input元素，則執行相應的邏輯
            // 例如，你可以在這裡添加處理邏輯或返回特定值
            return true;
        } else {
            // 顯示模態框
            $(".approval_opinionarea").css("display", "block");
            clickedButton = button; // 儲存點擊的按鈕
            alert("是否已依卡號或密碼設定門禁權限")
            return false;
        }
    }
    else {
        // return true;
        var form = $(button).closest('form'); // 找到最接近的form元素
        var inputExists = form.find('input[name="approval_opinion"]').length > 0; // 檢查input元素是否存在
        if (inputExists) {
            // 如果存在名為"complaint_departments"的input元素，則執行相應的邏輯
            // 例如，你可以在這裡添加處理邏輯或返回特定值
            return true;
        } else {
            // 顯示模態框
            $(".approval_opinionarea").css("display", "block");
            clickedButton = button; // 儲存點擊的按鈕
            return false;
        }
    }
}