# Integrating Google Colab Stable Diffusion with CONTRA

This guide explains how to use the `contra_stablediffusion_api.py` script to set up a Stable Diffusion model on Google Colab and integrate it with your CONTRA project.

## Step 1: Run the Stable Diffusion API on Google Colab

1. **Upload the script to Google Colab**:
   - Go to [Google Colab](https://colab.research.google.com/)
   - Create a new notebook
   - Copy the contents of `contra_stablediffusion_api.py` into a cell
   - Alternatively, you can upload the file directly to Colab

2. **Run the script**: 
   - Execute the cell and wait for the model to load
   - The script will install required dependencies, set up Stable Diffusion, and create a Gradio interface
   - It will automatically generate a public URL for your API endpoint

3. **Get the endpoint URL**:
   - Look for output that says `Running on public URL: https://xxxx.gradio.live`
   - Copy this URL - you'll need it for the next step

## Step 2: Update your CONTRA environment configuration

1. **Update the `.env.new` file**:
   - Open the `.env.new` file created in this project
   - Replace `https://your-gradio-url-from-colab-here` with the URL you copied from Colab

2. **Apply the new environment configuration**:
   ```
   move .env.new .env -Force
   ```

3. **Verify the configuration**:
   - Make sure your `.env` file contains:
     ```
     SD_GRADIO_ENDPOINT=https://your-actual-gradio-url-from-colab
     USE_CUSTOM_GRADIO=true
     ```

## Step 3: Run the CONTRA application

1. **Start the application**:
   ```
   python run.py
   ```

2. **Test image generation**:
   - Navigate to http://localhost:5000 in your browser
   - Enter a topic and click "Generate"
   - The application should now use your Colab-hosted Stable Diffusion API for image generation

## Important Notes

- **Colab session timeout**: Google Colab sessions will disconnect after a period of inactivity. When this happens, you'll need to:
  1. Rerun the script in Colab
  2. Get the new URL (it changes each time)
  3. Update your `.env` file with the new URL

- **Resource limitations**: Free Colab instances have GPU time limits. For extended use, consider:
  - Using Colab Pro
  - Setting up Stable Diffusion locally
  - Using a cloud-based alternative

- **Error handling**: If you see image generation errors, check:
  1. That your Colab instance is still running
  2. That the Gradio URL is still active
  3. The API endpoint in your `.env` file matches the current Colab URL 