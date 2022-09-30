import pandas as pd

with pd.ExcelWriter('output.xlsx', engine="xlsxwriter") as writer:
    workbook = writer.book
    workbook.add_worksheet()
    workbook.add_worksheet()
    worksheet1 = workbook.sheetnames['Sheet1']
    worksheet2 = workbook.sheetnames['Sheet2']
    worksheet1.insert_image('A1', 'reportFig.png')
    worksheet2.insert_image('A1', 'reportFig1.png')
    pass
