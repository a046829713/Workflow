function generateExcel() {

    if (document.querySelector('svg')) {    // 創建Excel數據數組
        var data = [
            ['料號'],

        ];
        for (var i = 0; i < leadtimedata.length; i++) {
            data.push([leadtimedata[i]]);
        }

        // 創建工作簿對象
        var workbook = XLSX.utils.book_new();

        // 將數據添加到工作表中
        var worksheet = XLSX.utils.aoa_to_sheet(data);
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');

        // 將Excel文件下載到本地
        XLSX.writeFile(workbook, `${document.querySelector('#motherpd').value}.xlsx`);
    }

}