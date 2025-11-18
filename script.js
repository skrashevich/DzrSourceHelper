function exportTabToJson(tab) {
  var body = tab.getBody();
  
  var root = {};
  var stack = [root];
  var currentLevel = 0;
  
  var headingLevels = {
    [DocumentApp.ParagraphHeading.HEADING1]: 1,
    [DocumentApp.ParagraphHeading.HEADING2]: 2,
    [DocumentApp.ParagraphHeading.HEADING3]: 3,
    [DocumentApp.ParagraphHeading.HEADING4]: 4,
    [DocumentApp.ParagraphHeading.HEADING5]: 5,
    [DocumentApp.ParagraphHeading.HEADING6]: 6
  };
  
  function extractTableData(table) {
    var tableData = [];
    for (var rowIndex = 0; rowIndex < table.getNumRows(); rowIndex++) {
      var row = table.getRow(rowIndex);
      var rowData = [];
      for (var cellIndex = 0; cellIndex < row.getNumCells(); cellIndex++) {
        var cellText = row.getCell(cellIndex).getText();
        rowData.push(cellText);
      }
      tableData.push(rowData);
    }
    return tableData;
  }
  
  var elements = body.getNumChildren();
  for (var i = 0; i < elements; i++) {
    var element = body.getChild(i);
    var type = element.getType();
    
    if (type === DocumentApp.ElementType.PARAGRAPH) {
      var paragraph = element.asParagraph();
      var headingType = paragraph.getHeading();
      var text = paragraph.getText().trim();
      Logger.log(text);
      
      if (headingType !== DocumentApp.ParagraphHeading.NORMAL) {
        var newLevel = headingLevels[headingType] || 0;
        while (newLevel <= currentLevel) {
          stack.pop();
          currentLevel = stack.length;
        }
        var newObj = { content: '', tables: []};
        var parent = stack[stack.length - 1];
        parent[text] = newObj;
        stack.push(newObj);
        currentLevel = newLevel;
        
      } else if (stack.length > 0) {
        // Обычный текст
        var currentObj = stack[stack.length - 1];
        if (currentObj.content) {
          currentObj.content += '\n' + text;
        } else {
          currentObj.content += '\n' + text;
        }
      }
      
    } else if (type === DocumentApp.ElementType.TABLE && stack.length > 0) {
      var currentObj = stack[stack.length - 1];
      var tableData = extractTableData(element.asTable());
      currentObj.tables.push(tableData); 
    }
  }
  
  // Trim content
  function trimContent(obj) {
    if (obj.content) obj.content = obj.content.trim();
    for (var key in obj) {
      if (typeof obj[key] === 'object' && obj[key] !== null) {
        trimContent(obj[key]);
      }
    }
  }
  trimContent(root);
  
  // Очистка пустых полей (tables, lists, content)
  function cleanEmptyFields(obj) {
    if (obj.tables && obj.tables.length === 0) delete obj.tables;
    if (obj.lists && obj.lists.length === 0) delete obj.lists;
    if (obj.content === '') delete obj.content;
    for (var key in obj) {
      if (typeof obj[key] === 'object' && obj[key] !== null) {
        cleanEmptyFields(obj[key]);
      }
    }
  }
  cleanEmptyFields(root);
  return root;
}

function exportDocToJson() {
  var doc = DocumentApp.getActiveDocument().getTabs();
  const tabs = [];
  for (var i = 3; i < doc.length; i++) {
    var tab = exportTabToJson(DocumentApp.getActiveDocument().getTab(doc[i].getId()).asDocumentTab());
    tabs.push(tab);
  }
  return tabs;
}

function doGet() {
  var data = exportDocToJson();
  Logger.log(data)
  if(!data) {
    data = '';
  }
  return ContentService.createTextOutput(JSON.stringify(data));
}