# 🚀 GitHub Upload Guide

This guide will walk you through uploading your ComfyUI Novel Nodes Collection to GitHub.

## 📋 Prerequisites

- A GitHub account (create one at https://github.com if you don't have one)
- Git installed on your computer (already done ✅)

## 🎯 Step-by-Step Instructions

### Step 1: Create a New Repository on GitHub

1. Go to https://github.com
2. Log in to your account
3. Click the **"+"** icon in the top-right corner
4. Select **"New repository"**

### Step 2: Configure Your Repository

Fill in the following details:

- **Repository name**: `comfyui-novel-nodes-collection` (or your preferred name)
- **Description**: `A comprehensive collection of ComfyUI custom nodes for transforming novels into cinematic video productions`
- **Visibility**: 
  - ✅ **Public** (recommended for sharing with the community)
  - ⬜ Private (if you want to keep it private initially)
- **Initialize repository**: 
  - ⬜ **DO NOT** check "Add a README file"
  - ⬜ **DO NOT** check "Add .gitignore"
  - ⬜ **DO NOT** check "Choose a license"
  
  (We already have these files!)

4. Click **"Create repository"**

### Step 3: Connect Your Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Navigate to your repository folder
cd "c:\Users\trini\Downloads\comfyui nodes\comfyui-novel-nodes-collection"

# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/comfyui-novel-nodes-collection.git

# Rename the branch to main (if needed)
git branch -M main

# Push your code to GitHub
git push -u origin main
```

### Step 4: Enter Your Credentials

When prompted:
- **Username**: Your GitHub username
- **Password**: Use a **Personal Access Token** (not your GitHub password)

#### How to Create a Personal Access Token:

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: `ComfyUI Nodes Upload`
4. Select scopes: Check **"repo"** (full control of private repositories)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)
7. Use this token as your password when pushing

### Step 5: Verify Upload

1. Go to your GitHub repository page
2. You should see all your files uploaded
3. The README.md will be displayed on the main page

## 🎨 Customizing Your Repository

### Update the README

Replace `YOUR_USERNAME` in the README.md with your actual GitHub username:

```bash
# In the repository folder
# Open README.md and replace all instances of YOUR_USERNAME
```

Or use this command:

```bash
# Replace YOUR_USERNAME with your actual username
(Get-Content README.md) -replace 'YOUR_USERNAME', 'your-actual-username' | Set-Content README.md
git add README.md
git commit -m "Update GitHub username in README"
git push
```

### Add Topics/Tags

On your GitHub repository page:

1. Click the ⚙️ icon next to "About"
2. Add topics: `comfyui`, `custom-nodes`, `ai`, `image-generation`, `novel`, `text-to-image`, `stable-diffusion`, `flux`
3. Save changes

### Enable Discussions (Optional)

1. Go to Settings → General
2. Scroll to "Features"
3. Check "Discussions"
4. This allows users to ask questions and share workflows

### Create a Release (Optional)

1. Click "Releases" on the right sidebar
2. Click "Create a new release"
3. Tag version: `v1.0.0`
4. Release title: `Initial Release - v1.0.0`
5. Description: Brief summary of features
6. Click "Publish release"

## 📝 Making Updates

When you make changes to your code:

```bash
# Navigate to your repository
cd "c:\Users\trini\Downloads\comfyui nodes\comfyui-novel-nodes-collection"

# Check what changed
git status

# Add all changes
git add .

# Commit with a message
git commit -m "Description of your changes"

# Push to GitHub
git push
```

## 🔧 Common Commands

```bash
# Check repository status
git status

# View commit history
git log --oneline

# Create a new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Pull latest changes
git pull

# View remote URL
git remote -v
```

## 🐛 Troubleshooting

### Authentication Failed

- Make sure you're using a Personal Access Token, not your password
- Check that the token has "repo" permissions
- Token might have expired - create a new one

### Push Rejected

```bash
# Pull the latest changes first
git pull origin main --rebase

# Then push again
git push
```

### Wrong Remote URL

```bash
# Remove the old remote
git remote remove origin

# Add the correct one
git remote add origin https://github.com/YOUR_USERNAME/comfyui-novel-nodes-collection.git
```

## 🌟 Promoting Your Repository

After uploading:

1. **Share on Reddit**: r/comfyui, r/StableDiffusion
2. **Share on Discord**: ComfyUI Discord server
3. **Add to ComfyUI Manager**: Submit a PR to the ComfyUI Manager registry
4. **Create a showcase**: Share example workflows and results
5. **Write a blog post**: Explain your nodes and use cases

## 📊 Repository Statistics

Once uploaded, you can track:
- ⭐ Stars (people who like your project)
- 👁️ Watchers (people following updates)
- 🔀 Forks (people who copied your project)
- 📈 Traffic (views and clones)

## ✅ Checklist

- [ ] Created GitHub repository
- [ ] Connected local repository to GitHub
- [ ] Pushed all files successfully
- [ ] Updated README with your username
- [ ] Added repository topics/tags
- [ ] Created initial release (optional)
- [ ] Enabled discussions (optional)
- [ ] Shared with the community

## 🎉 You're Done!

Your ComfyUI custom nodes are now on GitHub and ready to share with the world!

Repository URL format:
```
https://github.com/YOUR_USERNAME/comfyui-novel-nodes-collection
```

Users can now install with:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/YOUR_USERNAME/comfyui-novel-nodes-collection.git
```

---

**Need help?** Open an issue on GitHub or check the Git documentation at https://git-scm.com/doc
