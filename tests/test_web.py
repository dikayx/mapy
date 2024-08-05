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


# Test the CSRF token is included in the form
def test_csrf_token_in_form(client):
    response = client.get('/')
    assert b'name="csrf_token"' in response.data


# Test the CSRF token has a valid value
def test_csrf_token_value_print(client):
    response = client.get('/')
    csrf_token_regex = rb'<input\n\s*type="hidden"\n\s*name="csrf_token"\n\s*value="[^"]+"\n\s*/>'
    csrf_token = re.search(csrf_token_regex, response.data).group(0)
    assert csrf_token


# Test valid data submission
def test_valid_data_submission(client):
    valid_headers = """Return-Path: <mailings@mailings.gmx.net>
                            Authentication-Results:  gmx.net; dkim=pass header.i=@mailings.gmx.net
                            Received: from mout-csbulk.1and1.com ([212.227.15.53]) by mx-ha.gmx.net
                            (mxgmx103 [212.227.17.5]) with ESMTPS (Nemesis) id 1MeCZ5-1nWyOC0iSF-00bMu8
                            for <Max_Mustermann@gmx.de>; Thu, 30 Jun 2022 12:47:23 +0200
                            DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/simple; d=mailings.gmx.net;
                            s=isystem1; t=1656586043;
                            bh=zi4FqYIdpIwcsf+sK0WA75BbiA5zVTCs/dPw6mK+63Y=;
                            h=X-UI-Sender-Class:Date:To:From:Reply-To:Subject;
                            b=D/x4ENmFX26x0Yfir0uzyaDldP00MNpErNvYpU8FKs6E+QxC5a8hvWuvZNBvMkEp3
                            Jaui124uVl4eqGhgwHeeRht2KGErlPr90RwShXzHDTutfK8dE8iB8/Vnh/MUyWdJzE
                            AGicEqtR+Sbb3GA5tI0TjuT8AHeu2SjfW1+6pnPM=
                            X-UI-Sender-Class: b1815dde-56d5-42be-91f0-18350f97da04
                            Received: from esix-sender-gmx-bs04.ui-portal.com ([10.74.4.16]) by
                            mrs-csbulk.1and1.com (mrsbulk009 [172.19.128.198]) with ESMTPSA (Nemesis) id
                            0LgNmu-1nJRz43zSG-00nlFe for < Max_Mustermann@gmx.de>; Thu, 30 Jun 2022
                            12:47:23 +0200
                            Date: Thu, 30 Jun 2022 12:47:22 +0200
                            To: Max_Mustermann@gmx.de
                            From: GMX Magazin <mailings@mailings.gmx.net>
                            Reply-To: mailings@gmxnet.de
                            Subject: Ihr Stromtarif + iPad oder 4K-TV
                            Message-ID: <E5-3hqyee3o-elaine/10/534-004a6uhu@esix-sender-gmx-bs04.ui-portal.com>
                            …"""

    response = client.get('/')
    csrf_token_regex = rb'<input\n\s*type="hidden"\n\s*name="csrf_token"\n\s*value="[^"]+"\n\s*/>'
    # Extract only the value of the CSRF token
    csrf_token = re.search(csrf_token_regex, response.data).group(0)
    csrf_token = csrf_token.split(b'value="')[1].split(b'"')[0]

    post_response = client.post('/', data={'headers': valid_headers, 'csrf_token': csrf_token}, follow_redirects=True)
    assert post_response.status_code == 200


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
