from rest_framework import serializers



class AssetDataSerializer(serializers.Serializer):
    asset_id = serializers.CharField(max_length=100, label="Asset ID")  # 財產編號
    asset_type = serializers.CharField(max_length=100, label="Asset Type")  # 類型
    item = serializers.CharField(max_length=100, label="Item")  # 項目
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, label="Amount")  # 金額
    acquisition_date = serializers.DateField(label="Acquisition Date")  # 取得日期
    disposal_reason = serializers.CharField(max_length=100, label="Disposal Reason")  # 報廢原因
