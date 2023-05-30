import axios from 'axios';

function hello(person: string) {
  return "hello, " + person;
}
// var user = "foo";
// document.body.textContent = hello(user);

async function get_num() {
  try {
    const response = await axios.get('localhost:5000/num');
    const data = response.data;
    // Process the data returned from the API endpoint
    console.log(data);
    return data;
  } catch (error) {
    // Handle any errors that occurred during the request
    console.error('Error:', error.message);
  }
}

get_num().then((number) => {
  console.log('Got number: ' + number);
});
