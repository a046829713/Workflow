$(document).ready(function () {
    // 預設新增一組語言選擇與能力等級選擇
    var abilities = ['聽', '說', '讀', '寫'];
    var levels = [
        { text: '選擇你的能力', value: '' },
        { text: '略懂', value: '略懂' },
        { text: '中等', value: '中等' },
        { text: '精通', value: '精通' },
    ];

    var languages = [
        { text: '選擇語言', value: '' },
        { text: '英文', value: '英文' },
        { text: '越南文', value: '越南文' },
        // 更多語言
    ];

    function addLanguage() {
        var languageSelect = $('<select>').addClass('form-select mb-2').attr('name', '語言種類');
        languages.forEach(function (language) {
            languageSelect.append($('<option>').val(language.value).text(language.text));
        });
        $('#language-abilities').append(languageSelect);

        var abilityContainer = $('<div>').addClass('d-flex justify-content-around mb-2');
        abilities.forEach(function (ability) {
            var label = $('<label>').addClass('form-label text-success').text(ability);
            var select = $('<select>').addClass('form-select me-3').attr('name', '語言能力');
            levels.forEach(function (level) {
                select.append($('<option>').val(level.value).text(level.text));
            });
            abilityContainer.append(label, select);
        });
        $('#language-abilities').append(abilityContainer);
    }

    $('#add-language').click(function () {
        addLanguage();
    });

    if ($("#language-abilities").length) {
        addLanguage();
    }


});


function changeFormAction(action, submitURL, SaveURL) {
    // 用來改變表單所要提交的網址
    var form = document.querySelector("form");
    if (action == 'submit') {
        form.action = submitURL
    } else if (action == 'save') {
        form.action = SaveURL

    }
    form.submit();
    
}