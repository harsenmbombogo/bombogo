import cloudinary
import cloudinary.uploader
import cloudinary.api

# Set up your Cloudinary credentials
cloudinary.config(
    cloud_name = "dbngtm6yy",  # Replace with your cloud name
    api_key = "169688719445956",        # Replace with your API key
    api_secret = "sK5BCH2GKvYmLfWBDL4mMno2TLg"   # Replace with your API secret
)

# Upload an image to Cloudinary
def upload_image(image_path):
    try:
        response = cloudinary.uploader.upload(image_path)
        print("Upload successful!")
        print("Image URL:", response['url'])
        return response
    except Exception as e:
        print("Error uploading image:", e)

# Manipulate the image (resize example)
def manipulate_image(public_id):
    try:
        # Resize the image to 300x300 pixels
        image_url = cloudinary.CloudinaryImage(public_id).build_url(width=300, height=300, crop="fill")
        print("Manipulated Image URL:", image_url)
    except Exception as e:
        print("Error manipulating image:", e)

# Delete an image from Cloudinary
def delete_image(public_id):
    try:
        cloudinary.uploader.destroy(public_id)
        print("Image deleted successfully.")
    except Exception as e:
        print("Error deleting image:", e)

# Main function to demonstrate the process
if __name__ == "__main__":
    image_path = "C:/Users/Lenovo Ideapad 3/Pictures/mpesa.jpg"  # Path to the image you want to upload

    # Upload image
    upload_response = upload_image(image_path)
    
    if upload_response:
        public_id = upload_response['public_id']
        
        # Manipulate the uploaded image (resize it)
        manipulate_image(public_id)
        
        # Optionally, delete the image after manipulation
        # delete_image(public_id)
