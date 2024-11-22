function HandleNumberToCall() {
    // 用来检查查询的职务说明书，用户是否有打正确
    var checktext = $('#select2-id_resource_no-container').text();

    if (checktext && checktext !== '--') {
        $('#href_url_to_check').attr('href', '/form_information_finish/' + checktext.split('/')[0]);
    } else {
        alert("請選擇要查詢的職務說明書");
        return false; // 如果没有选择有效的选项，返回false
    }
}








$(document).ready(function () {
    // 當人員增補原因有所異動的時候
    $("#add_people_reason_choice").on("change", function () {
        let selectedValue = $(this).val();
        if (selectedValue == '短期需求') {
            $('#short_term_duration_area').show()
        } else {
            $('#short_term_duration_area').hide()
            $('#short_term_duration').val('')
        }
    });

    // 年齡有所異動的時候
    $("#age_Department").change(function () {
        var ageInput = $("#age_Department_area");
        if ($(this).val() == "年齡限制") {
            ageInput.show();
        } else {
            ageInput.hide();
            ageInput.val("");  // 如果用户选择了“不拘”，清空年龄输入字段的值
        }
    });

    // 學歷有所異動的時候
    $(".education_level-choice ").on("change", function () {
        if ($(this).val() == '學歷限制') {
            $("#custom_education_level").show();

        } else {
            $("#custom_education_level").hide();
            $("#custom_education_level input[type='checkbox']").prop('checked', false);

        }
    });


    $(".work_experience-choice").on("change", function () {
        var jobTitleInput = $("#job_title");
        var workYearsInput = $("#work_years");
        var workYearsLabel = $("#work_years_label");


        if ($(this).val() == "希望具備") {
            jobTitleInput.show();
            workYearsInput.show();
            workYearsLabel.show();
            jobTitleInput.prop('required', true);
            workYearsInput.prop('required', true);
        } else {
            jobTitleInput.hide();
            jobTitleInput.val("");
            workYearsInput.hide();
            workYearsInput.val("");
            workYearsLabel.hide();
            jobTitleInput.prop('required', false);
            workYearsInput.prop('required', false);
        }
    });








    // 刪除===================================================================================
    $(".clear_language_form").on('click', function () {
        // 清空當前表單的所有輸入框資料
        let formContainer = $(this).closest('.language_group');
        formContainer.find('select').val('');
        formContainer.find('select').prop('required', false);
        // 將這個已清空的表單移到所有表單的最後面
        formContainer.addClass("hiddenlanguage")
        formContainer.parent().appendTo(formContainer.parent().parent());

    });

    $(".clear_tool_form").on('click', function () {
        let toolformContainer = $(this).closest('.tool_container');
        toolformContainer.find('select[name*="first_level"]').val('').trigger('change');
        toolformContainer.find('select[name*="second_level"]').val('').trigger('change');
        toolformContainer.find('select[name*="third_level"]').val('').trigger('change');
        toolformContainer.addClass("hiddentool")
        toolformContainer.appendTo(toolformContainer.parent());
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


    $('#addToolform').on('click', function () {
        showHiddenForm('.hiddentool', function () { });
    });


    $('Form').submit(function (e) {
        // 表單檢查定義
        if ($('.language_group:not(.hiddenlanguage)').length > 0) {
            let languagecheck = true
            $('.language_group:not(.hiddenlanguage)').each(function () {
                let islanguage = $(this).find('select[name*="language"]').val();
                let islisten = $(this).find('select[name*="listen"]').val();
                let isspeak = $(this).find('select[name*="speak"]').val();
                let isread = $(this).find('select[name*="read"]').val();
                let iswrite = $(this).find('select[name*="write"]').val();
                if (!islanguage && (islisten || isspeak || isread ||iswrite)) {
                    languagecheck = false
                }
            })

            if (languagecheck) {
                alert("送出成功")
            } else {
                alert("語文類別尚未選擇")
                // 阻止表单的默认提交行为
                e.preventDefault();
                return;
            }
        }
    });
});
