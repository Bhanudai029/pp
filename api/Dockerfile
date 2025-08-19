# Use an official Node.js runtime as a parent image
FROM node:18-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install app dependencies
RUN npm install

# Install puppeteer browser
RUN npx puppeteer browsers install chrome

# Copy the rest of the application code to the working directory
COPY . .

# Make port 10000 available to the world outside this container
EXPOSE 10000

# Define the command to run your app
CMD [ "node", "server.js" ]