function toggleDepartmentRequiredState(isRequired) {
    $("#custom-department input").prop('required', isRequired);
}

function toggleCertificatesRequiredState(isRequired) {
    $("#custom_certificates input").prop('required', isRequired);
}

// 管理責任欄位隱藏
function toggleManagement_responsibilityRequiredState(isRequired) {
    $("#custom_management_responsibility input").prop('required', isRequired);

}


function change_required() {
    $('.hidden .job_responsibilities_time').prop('required', false);
    $('.hidden .work_hours_input').prop('required', false);
    $('.hidden .time_frequency').prop('required', false);

    $('.job_responsibilities_time').not('.hidden .job_responsibilities_time').prop('required', true);
    $('.work_hours_input').not('.hidden .work_hours_input').prop('required', true);
    $('.time_frequency').not('.hidden .time_frequency').prop('required', true);
}

function change_tool_required() {
    // 原本有用的,後來使用檢查機制
    console.log('change_tool_required called');
}



function change_skill_required() {
    console.log('change_skill_required called');
}

function showHiddenForm(selector, callback) {
    var $hiddenForms = $(selector);
    if ($hiddenForms.length > 0) {
        var $form = $hiddenForms.first();
        $form.removeClass(selector.substring(1));  // remove the dot from the class selector
        if (typeof callback === "function") {
            callback();  // call the callback function if it is provided and is a function
        }
    }
}



function updatePercentageTotal() {
    // 更新計算的結果
    let totalPercentage = 0;
    let count_all = 0

    $('.container.value_have input[name*="work_hours_percentage"]').each(function () {
        let value = parseFloat($(this).val());

        if (!isNaN(value)) {
            totalPercentage += value;
            count_all += 1;
        }
    });

    $('#percentageTotal').text(totalPercentage);


    if (totalPercentage == 100 && count_all >= 6) {
        $('.color_show_time').removeClass("text-danger")
        $('.color_show_time').addClass("")
    } else {
        $('.color_show_time').removeClass("")
        $('.color_show_time').addClass("text-danger")
    }
}



function checkTool(e) {
    var isToolValid = true;
    $('.first_level, .second_level, .third_level').not('.hiddentool .first_level, .hiddentool .second_level, .hiddentool .third_level').each(function () {
        if (!$(this).val()) {
            isToolValid = false;
        }
    });
    if (!isToolValid) {
        e.preventDefault();
        alert('工具種類尚未填寫完全');
        return
    }
}
function checkSkill(e) {
    var isToolValid = true;
    $('.skill_first_level, .skill_second_level, .skill_third_level').not('.hiddenskill .skill_first_level, .hiddenskill .skill_second_level, .hiddenskill .skill_third_level').each(function () {
        if (!$(this).val()) {
            isToolValid = false;
        }
    });
    if (!isToolValid) {
        e.preventDefault();
        alert('工作技能尚未填寫完全');
        return
    }
}

function checkValueifexits() {
    // 檢查所有的值是否存在
    let isvalue = false
    let jobTimeEstimation = $('textarea[name*="job_function_and_responsibilities_time_estimation"]');
    let workHoursPercentage = $('textarea[name*="work_hours_percentage"]');
    let timeFrequency = $('textarea[name*="time_frequency"]');  // 改成 select
    // 遍历 jobTimeEstimation 集合中的每个元素
    jobTimeEstimation.each(function (index, element) {
        // 'element' 是当前遍历到的原生 DOM 元素
        // 可以使用 $(element) 将其转换为 jQuery 对象，以便使用 jQuery 方法
        let value = $(element).val();
        if (value) { // 检查值是否存在
            isvalue = true;
        }
    });
    // 遍歷所有的表單
    if (isvalue) {
        $('.container.value_have').each(function (index) {
            // 不知道為甚麼time_frequency 必須要手動強制才能添加required
            $(this).find('select[name*="time_frequency"]').attr('required', true);  // 為 timeFrequency 添加 required 屬性
            let isEmpty = true;
            let jobTimeEstimation = $(this).find('input[name*="job_function_and_responsibilities_time_estimation"]').val();
            let workHoursPercentage = $(this).find('input[name*="work_hours_percentage"]').val();
            let timeFrequency = $(this).find('select[name*="time_frequency"]').val();  // 改成 select

            // 如果表單是第7個或更多，且內部的特定欄位都是空的            
            if (index >= 0) {
                if (jobTimeEstimation || workHoursPercentage || timeFrequency) {
                    isEmpty = false;
                }
                if (isEmpty) {
                    $(this).find('.delete-form-btn').click()
                }
            }
        });

    }

}

$(document).ready(function () {
    // 初始化區域 ============================================================================================
    // 綁定事件用
    $('.container.value_have input[name*="work_hours_percentage"]').on('input', updatePercentageTotal);

    // Initial calculation
    updatePercentageTotal();


    // 改變顏色
    $('.first_level, .second_level, .third_level').change(function () {
        // 当任一select元素改变时，检查所有的select元素
        $('.first_level, .second_level, .third_level').each(function () {
            if ($(this).val()) {  // 如果有值被选中
                // 重置边框颜色为默认
                $(this).next('.select2').find('.select2-selection').css('border', '1px solid #ccc');
            } else {  // 如果没有值被选中
                // 设置边框颜色为红色
                $(this).next('.select2').find('.select2-selection').css('border', '1px solid red');
            }
        });
    });

    // 改變顏色
    $('.skill_first_level, .skill_second_level, .skill_third_level').change(function () {
        // 当任一select元素改变时，检查所有的select元素
        $('.skill_first_level, .skill_second_level, .skill_third_level').each(function () {
            if ($(this).val()) {  // 如果有值被选中
                // 重置边框颜色为默认
                $(this).next('.select2').find('.select2-selection').css('border', '1px solid #ccc');
            } else {  // 如果没有值被选中
                // 设置边框颜色为红色
                $(this).next('.select2').find('.select2-selection').css('border', '1px solid red');
            }
        });
    });
    // 綁定change區域 ============================================================================================
    // 這邊的網址不能使用模板語言
    // id_Tool_expert思考上非異步綁定,设置每个 first_level 选择框的更改事件处理程序
    $('select[id^="id_Tool_expert"][id$="-first_level"]').change(function () {
        var selectedValue = $(this).val();
        // 找到相应的 second_level 选择框
        var secondLevelSelect = $(this).parent().find('select[id$="-second_level"]');
        // 发送 AJAX 请求以获取 second_level 的选项        
        $.get("/HumanResource/get_level_ajax", { first_level: selectedValue }, function (data) {
            secondLevelSelect.empty();
            $.each(data.second_level, function (key, value) {
                secondLevelSelect.append($('<option></option>').attr('value', key).text(value));
            });            
        });

        // 清空選項3
        $(this).parent().find('select[id$="-third_level"]').empty();
    });

    // 为 second_level 设置更改事件处理程序，类似于上述代码
    $('select[id^="id_Tool_expert"][id$="-second_level"]').change(function () {
        var selectedValue = $(this).val();
        var firstLevelValue = $(this).parent().find('select[id$="-first_level"]').val();
        var thirdLevelSelect = $(this).parent().find('select[id$="-third_level"]');
        $.get("/HumanResource/get_level_ajax", { first_level: firstLevelValue, second_level: selectedValue }, function (data) {
            thirdLevelSelect.empty();
            $.each(data.third_level, function (key, value) {
                thirdLevelSelect.append($('<option></option>').attr('value', key).text(value));
            });
        });
    });
    // id_Tool_expert==================================================











    // 綁定click區域 ============================================================================================
    $('#addForm').on('click', function () {
        showHiddenForm('.hidden', change_required);
    });

    $('#addToolform').on('click', function () {
        showHiddenForm('.hiddentool', change_tool_required);
    });

    $('#addskillform').on('click', function () {
        showHiddenForm('.hiddenskill', change_skill_required);
    });


    // 刪除===================================================================================
    $(".clear_tool_form").on('click', function () {
        let toolformContainer = $(this).closest('.tool_container');
        toolformContainer.find('select[name*="first_level"]').val('').trigger('change');
        toolformContainer.find('select[name*="second_level"]').val('').trigger('change');
        toolformContainer.find('select[name*="third_level"]').val('').trigger('change');
        // 将这个已清空的表单移到所有表单的最后面
        toolformContainer.addClass("hiddentool")
        toolformContainer.appendTo(toolformContainer.parent());

        change_tool_required()
    });


    $(".clear_skill_form").on('click', function () {
        let toolformContainer = $(this).closest('.skill_container');
        toolformContainer.find('select[name*="skill_first_level"]').val('').trigger('change');
        toolformContainer.find('select[name*="skill_second_level"]').val('').trigger('change');
        toolformContainer.find('select[name*="skill_third_level"]').val('').trigger('change');

        // // 將這個已清空的表單移到所有表單的最後面
        toolformContainer.addClass("hiddenskill")
        toolformContainer.appendTo(toolformContainer.parent());
    });

    $(".clear_language_form").on('click', function () {
        // 清空當前表單的所有輸入框資料
        let formContainer = $(this).closest('.language_group');
        formContainer.find('select').val('');
        formContainer.find('select').prop('required', false);
        // 將這個已清空的表單移到所有表單的最後面
        formContainer.addClass("hiddenlanguage")
        formContainer.parent().appendTo(formContainer.parent().parent());

    });
    // 這是刪除專用按鈕 用來清空資料重新排序
    $('.delete-form-btn').on('click', function () {
        // 清空當前表單的所有輸入框資料
        let formContainer = $(this).closest('.container');
        formContainer.find('input, select, textarea').val('');

        // 將這個已清空的表單移到所有表單的最後面
        formContainer.addClass("hidden")
        formContainer.appendTo(formContainer.parent());

        // 重新排序表單的編號
        $('.container.value_have').each(function (index) {
            $(this).find('.col-md-2.text-center').text((index + 1) + '.');
        });

        updatePercentageTotal();
        change_required()
    });

    // 新增===================================================================================
    $('#add_language').on('click', function () {
        // 获取所有隐藏的表单
        var $hiddenForms = $('.hiddenlanguage');
        // 如果有隐藏的表单，则显示第一个隐藏的表单
        if ($hiddenForms.length > 0) {
            var $form = $hiddenForms.first();
            $form.removeClass('hiddenlanguage');
        }
    });


})
