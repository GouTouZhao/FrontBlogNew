const axios = require('axios');
axios.post('http://127.0.0.1:10002/review/get_course_list', {
    base: {},
    college_id: 0,
    status: 1,
    page: 1,
    page_size: 100
}).then(res => console.log(JSON.stringify(res.data.data.list.map(c => c.course_id), null, 2))).catch(err => console.error(err.message));
