const data = '{"members": [{"user_id": 722123884732252199}], "nicknames": {"722123884732252199": "Nick"}}';
const fixedData = data.replace(/"([a-zA-Z0-9_]*id)":\s*(\d{15,20})/gi, '"$1":"$2"');
console.log(fixedData);
console.log(JSON.parse(fixedData));
