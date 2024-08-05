import re


# Test if the index page is accessible
def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<title>MAPy | E-Mail Analyzer</title>' in response.data
    assert b'<form method="POST" id="analyzeForm">' in response.data


# No other routes should be accessible
def test_404_page(client):
    response = client.get('/invalid')
    assert response.status_code == 404


# Test if the title of the page is correct
def test_index_title(client):
    response = client.get('/')
    title_regex = rb'<title>\s*MAPy \| E-Mail Analyzer\s*</title>'
    assert bool(re.search(title_regex, response.data))


# Test if the submit page form elements are rendered correctly
def test_submit_form_elements(client):
    response = client.get('/')
    assert b'<textarea' in response.data
    assert b'name="headers"' in response.data
    assert b'id="submitButton"' in response.data
    assert b'Paste the email data here...' in response.data


# Test the CSRF token is included and has a value
def test_csrf_token_value_print(client):
    response = client.get('/')
    assert b'name="csrf_token"' in response.data
    csrf_token_regex = rb'<input\n\s*type="hidden"\n\s*name="csrf_token"\n\s*value="[^"]+"\n\s*/>'
    csrf_token = re.search(csrf_token_regex, response.data).group(0)
    assert csrf_token


# Test invalid data submission
def test_invalid_data_submission(client):
    invalid_headers = "Not a valid email header"
    response = client.get('/')
    csrf_token_regex = rb'<input\n\s*type="hidden"\n\s*name="csrf_token"\n\s*value="[^"]+"\n\s*/>'
    csrf_token = re.search(csrf_token_regex, response.data).group(0)
    csrf_token = csrf_token.split(b'value="')[1].split(b'"')[0]

    post_response = client.post('/', data={'headers': invalid_headers, 'csrf_token': csrf_token}, follow_redirects=True)
    assert post_response.status_code == 200


# Test that the spinner is present and hidden by default
def test_spinner_presence(client):
    response = client.get('/')
    assert b'id="spinner"' in response.data
    assert b'display: none' in response.data


# Test JavaScript interactions
def test_javascript_link(client):
    response = client.get('/')
    assert b'<script src="' in response.data
    assert b'js/submit.js' in response.data


# Test multiple requests to ensure no session issues
def test_multiple_requests(client):
    for _ in range(10):
        response = client.get('/')
        assert response.status_code == 200
        assert b'<title>MAPy | E-Mail Analyzer</title>' in response.data
