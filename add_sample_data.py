#!/usr/bin/env python
import mysql.connector

def add_sample_data():
    try:
        conn = mysql.connector.connect(
            host='localhost', 
            user='root', 
            password='', 
            database='grade_sheet1'
        )
        cursor = conn.cursor()
        
        print("Adding sample data...")
        
        # Add sample users
        cursor.execute("""
            INSERT INTO users (username, email, name, arname, nickname, arnickname, role, phone, gender, password, create_datetime, seen_status, designation, teamunit, citycountry, languages, reportingmanager, projects, doj, country, subscription, studid, `TO`) 
            VALUES 
            ('john_doe', 'john@example.com', 'John Doe', 'جون دو', 'John', 'جون', 'Student', '1234567890', 'Male', 'password123', NOW(), 1, 'Student', 'IT', 'New York, USA', 'English', 'Dr. Smith', 'AI Project', '2023-01-15', 'USA', 'Premium', 'STU001', 'john_doe'),
            ('jane_smith', 'jane@example.com', 'Jane Smith', 'جين سميث', 'Jane', 'جين', 'Student', '0987654321', 'Female', 'password123', NOW(), 1, 'Student', 'IT', 'London, UK', 'English', 'Prof. Johnson', 'Web Development', '2023-02-20', 'UK', 'Premium', 'STU002', 'jane_smith'),
            ('admin_user', 'admin@example.com', 'Admin User', 'مدير المستخدم', 'Admin', 'مدير', 'Admin', '5555555555', 'Male', 'admin123', NOW(), 1, 'Administrator', 'Management', 'Dubai, UAE', 'English, Arabic', 'CEO', 'System Management', '2022-01-01', 'UAE', 'Enterprise', 'ADM001', 'admin_user')
        """)
        
        # Add sample encyclopedia books (simplified)
        cursor.execute("""
            INSERT INTO library_encyclopedia_book (title, author_id, description, publication_date, isbn, cover_image, edition_number, file, slug, pdf_page_count, total_ratings, average_rating, bookmark_count, download_count, created_at, updated_at) 
            VALUES 
            ('Encyclopedia of Science', 1, 'Comprehensive guide to scientific concepts and discoveries', '2020-01-15', '978-1234567890', 'science_cover.jpg', 1, '/books/science_encyclopedia.pdf', 'encyclopedia-of-science', 500, 25, 4.5, 15, 120, NOW(), NOW()),
            ('World History Encyclopedia', 2, 'Complete history of human civilization from ancient times to modern era', '2019-06-20', '978-0987654321', 'history_cover.jpg', 1, '/books/history_encyclopedia.pdf', 'world-history-encyclopedia', 800, 30, 4.7, 22, 180, NOW(), NOW()),
            ('Medical Encyclopedia', 3, 'Comprehensive medical reference guide for healthcare professionals', '2021-03-10', '978-1122334455', 'medical_cover.jpg', 1, '/books/medical_encyclopedia.pdf', 'medical-encyclopedia', 1200, 18, 4.3, 12, 95, NOW(), NOW())
        """)
        
        # Add sample authors (simplified)
        cursor.execute("""
            INSERT INTO library_authors (name, bio, profession, profile_pic, wikipedia, youtube, X_twitter, slug, created_at, updated_at) 
            VALUES 
            ('Dr. Smith', 'Renowned scientist and researcher in physics', 1, 'dr_smith.jpg', 'https://wikipedia.org/dr_smith', 'https://youtube.com/dr_smith', 'https://twitter.com/dr_smith', 'dr-smith', NOW(), NOW()),
            ('Prof. Johnson', 'Distinguished historian specializing in world history', 2, 'prof_johnson.jpg', 'https://wikipedia.org/prof_johnson', 'https://youtube.com/prof_johnson', 'https://twitter.com/prof_johnson', 'prof-johnson', NOW(), NOW()),
            ('Dr. Williams', 'Medical researcher and healthcare expert', 3, 'dr_williams.jpg', 'https://wikipedia.org/dr_williams', 'https://youtube.com/dr_williams', 'https://twitter.com/dr_williams', 'dr-williams', NOW(), NOW())
        """)
        
        # Add sample courses
        cursor.execute("""
            INSERT INTO newcourse (CourseName, nick_name, CourseDate, CourseCode, StudentNames, CourseManager, file_name, Instructor, value_enter, departmentId, gradutaion) 
            VALUES 
            ('Introduction to Computer Science', 'CS101', '2023-09-01', 101, 'John Doe, Jane Smith', 'Dr. Brown', 'cs101.pdf', 'Dr. Brown', 'active', 'IT', '2024'),
            ('Advanced Mathematics', 'MATH201', '2023-09-15', 201, 'Admin User', 'Prof. Davis', 'math201.pdf', 'Prof. Davis', 'active', 'Math', '2024'),
            ('Creative Writing Workshop', 'WRIT101', '2023-10-01', 301, 'John Doe', 'Ms. Wilson', 'writ101.pdf', 'Ms. Wilson', 'active', 'Arts', '2024')
        """)
        
        conn.commit()
        print("✅ Sample data added successfully!")
        
        # Verify the data
        print("\nVerifying data:")
        cursor.execute("SELECT COUNT(*) FROM users")
        print(f"Users: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM library_encyclopedia_book")
        print(f"Encyclopedia books: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM library_authors")
        print(f"Authors: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM newcourse")
        print(f"Courses: {cursor.fetchone()[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error adding sample data: {e}")

if __name__ == "__main__":
    add_sample_data() 