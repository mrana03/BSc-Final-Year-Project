import pytest
from app import app, db, User, Consultant, Project


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


def test_login(client):
    response = client.post('/', data={'username': 'testuser', 'password': 'testpassword'})
    assert response.status_code == 200
    assert b'Login successful!' in response.data


def test_login_invalid_credentials(client):
    response = client.post('/', data={'username': 'invaliduser', 'password': 'invalidpassword'})
    assert response.status_code == 200
    assert b'Invalid username or password. Please try again.' in response.data


def test_dashboard(client):
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Dashboard' in response.data


def test_client_dashboard(client):
    response = client.get('/client_dashboard')
    assert response.status_code == 302  # Redirect to login as user is not logged in


def test_submit_form(client):
    client.post('/', data={'username': 'admin', 'password': 'admin'})

    response = client.post('/submit_form', data={
        'client_name': 'TestClient',
        'project_name': 'TestProject',
        'project_reference': 'PR123',
        'client_contact_name': 'John Doe',
        'client_contact_email': 'john.doe@example.com',
        'project_description': 'Test project description',
        'project_deliverables': 'Test deliverables',
        'project_start_date': '2024-04-01',
        'project_end_date': '2024-04-30',
        'duration_in_days': '30',
        'consultants_requirement_details': 'Test requirements',
        'number_of_consultants_required': '3',
        'consultant_phone_number': '1234567890',
        'name_1': 'Consultant1',
        'phone_number_1': '1111111111',
        'company_name_1': 'Company1',
        'company_reg_number_1': 'CRN1',
        'address_1': 'Address1',
        'emp_id_1': 'EID1',
        'daily_rate_1': '500.0',
        'email_1': 'consultant1@example.com',
        'delivery_report_date_1': '2024-04-15',
        'project_number_1': 'PN1',
        'client_1': 'TestClient',
        'directorate_1': 'Directorate1',
        'consultancy_1': 'Consultancy1',
        'programme_area_1': 'ProgrammeArea1',
        'total_days_delivered_1': '10',
        'deliverables_status_1': 'On Track',
        'delivery_areas_1': 'Area1',
        'total_days_allocated_1': '15',
        'feb_days_1': '5',
        'mar_days_1': '5',
        'apr_days_1': '5',
        'may_days_1': '0',
        'june_days_1': '0',
        'remaining_days_1': '5',
        'delivery_areas_details_1': 'Details1',
        'comments_1': 'Test comments',
        'dependencies_1': 'Dependency1',
        'rag_1': 'Green',
        'output_1': 'Output1'
    })
    assert response.status_code == 302


def test_client_dashboard2(client):
    client.post('/', data={'username': 'client@example.com', 'password': 'password'})

    response = client.get('/client_dashboard2')
    assert response.status_code == 200
    assert b'Client Dashboard' in response.data


def test_create_user(client):
    client.post('/', data={'username': 'admin', 'password': 'admin'})

    response = client.post('/create_user', data={
        'username': 'newuser',
        'password': 'newpassword',
        'role': 'Client',
        'contact_info': 'test@example.com'
    })
    assert response.status_code == 302  # Redirect to dashboard


def test_consultant_dashboard2(client):
    client.post('/', data={'username': 'consultant@example.com', 'password': 'password'})

    response = client.get('/consultant_dashboard2')
    assert response.status_code == 200
    assert b'Consultant Dashboard' in response.data


def test_update_delivered_this_period(client):
    client.post('/', data={'username': 'consultant@example.com', 'password': 'password'})

    response = client.post('/update_delivered_this_period', json=[
        {'output': 'Updated output', 'value_to_trust': 'Updated value'}
    ])
    assert response.status_code == 200
