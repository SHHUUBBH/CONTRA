// CONTRA - Main Application JavaScript

// Global site properties
const ANIMATION_DURATION = 500; // ms

/**
 * Set up the expertise level selector
 */
function setupExpertiseLevel() {
    const levelSelector = document.getElementById('expertise_level');
    const levelDescription = document.getElementById('level-description');
    const levelDescriptionContent = document.querySelector('.level-description-content');
    const levelInfo = document.getElementById('level-info');
    
    if (levelSelector && levelDescription && levelDescriptionContent) {
        // Initialize with the default selected value
        updateLevelDescription(levelSelector.value);
        
        // Update when selection changes
        levelSelector.addEventListener('change', function() {
            updateLevelDescription(this.value);
        });
        
        // Show/hide description when clicking the info icon
        if (levelInfo) {
            levelInfo.addEventListener('click', function(e) {
                e.preventDefault();
                levelDescription.classList.toggle('active');
            });
        }
    }
    
    function updateLevelDescription(level) {
        // First, remove any existing level classes
        levelDescriptionContent.classList.remove('level-beginner', 'level-intermediate', 'level-advanced');
        
        // Add appropriate class
        levelDescriptionContent.classList.add(`level-${level}`);
        
        // Update content based on selected level
        let heading = '';
        let description = '';
        
        switch(level) {
            case 'beginner':
                heading = 'Beginner Level';
                description = 'Content will use very simple vocabulary and concepts, suitable for elementary/middle school students or those new to the topic.';
                break;
            case 'intermediate':
                heading = 'Intermediate Level';
                description = 'Content will use moderately advanced vocabulary and concepts, suitable for high school/undergraduate students or those with some familiarity with the topic.';
                break;
            case 'advanced':
                heading = 'Advanced Level';
                description = 'Content will use technical vocabulary and concepts, suitable for college graduates, professionals, or those with significant knowledge of the topic.';
                break;
            default:
                heading = 'Intermediate Level';
                description = 'Content will use moderately advanced vocabulary and concepts, suitable for high school/undergraduate students or those with some familiarity with the topic.';
        }
        
        // Update the HTML
        levelDescriptionContent.innerHTML = `
            <h4>${heading}</h4>
            <p>${description}</p>
        `;
    }
}

/**
 * Set up the generate form submission
 */
async function setupGenerateForm() {
    const generateForm = document.getElementById('generate-form');
    const loadingSection = document.getElementById('loading');
    const resultsSection = document.getElementById('results');
    const generateBtn = document.getElementById('generate-btn');
    
    // Set up tone selector to update UI preview
    const toneSelector = document.getElementById('tone');
    if (toneSelector) {
        // Apply tone class on selection change
        toneSelector.addEventListener('change', function() {
            // Remove any existing tone classes from body
            document.body.classList.remove(
                'tone-humorous', 
                'tone-dramatic', 
                'tone-poetic', 
                'tone-technical', 
                'tone-simple', 
                'tone-informative'
            );
            
            // Add the selected tone class
            const selectedTone = this.value;
            document.body.classList.add(`tone-${selectedTone}`);
});

        // Set initial tone class based on default selection
        const initialTone = toneSelector.value;
        document.body.classList.add(`tone-${initialTone}`);
    }
    
    if (!generateForm) {
        console.warn("Generate form not found");
        return;
    }
    
    generateForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
        // Get the topic input and validate
        const topicInput = document.getElementById('topic');
        const topic = topicInput ? topicInput.value.trim() : '';
        
        // Get the selected tone to use in results
        const toneSelector = document.getElementById('tone');
        const selectedTone = toneSelector ? toneSelector.value : 'informative';
        
        // Store selected tone in localStorage for persistence
        localStorage.setItem('selectedTone', selectedTone);
        
        if (!topic) {
            // Show error for empty topic
            const errorMsg = document.createElement('div');
            errorMsg.className = 'error-message';
            errorMsg.textContent = 'Please enter a topic';
            errorMsg.style.color = '#f44336';
            errorMsg.style.marginTop = '0.5rem';
            errorMsg.style.fontSize = '0.875rem';
            
            // Add error message after topic input if it doesn't exist already
            if (topicInput && !topicInput.parentNode.querySelector('.error-message')) {
                topicInput.parentNode.appendChild(errorMsg);
                
                // Highlight the input
                topicInput.style.borderColor = '#f44336';
                
                // Clear error after 3 seconds
                setTimeout(() => {
                    if (errorMsg.parentNode) {
                        errorMsg.parentNode.removeChild(errorMsg);
                        topicInput.style.borderColor = '';
                    }
                }, 3000);
            }
            
                return;
            }
            
        // Disable button and show loading state
        if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span>';
        }
        
        // Hide results, show loading
        resultsSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        loadingSection.innerHTML = `
            <div class="loading-container">
                <div class="loading-animation">
                    <div class="particle-container">
                        <div class="particle particle-1"></div>
                        <div class="particle particle-2"></div>
                        <div class="particle particle-3"></div>
                        <div class="particle particle-4"></div>
                    </div>
                    <div class="loading-spinner-ring">
                        <div class="loading-spinner-inner"></div>
                    </div>
                    <div class="loading-pulse"></div>
                </div>
                <div class="loading-text">
                    <h3 class="loading-title">Generating your experience</h3>
                    <div class="loading-steps">
                        <div class="loading-step active" data-step="1">Analyzing topic</div>
                        <div class="loading-step" data-step="2">Creating narrative</div>
                        <div class="loading-step" data-step="3">Generating visuals</div>
                        <div class="loading-step" data-step="4">Finalizing results</div>
                    </div>
                    <p class="loading-message">This process may take up to a minute depending on complexity</p>
                </div>
            </div>
        `;
    
        // Add the styles for the new loading animation
        const loadingStyles = document.createElement('style');
        loadingStyles.textContent = `
            .loading-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 2rem;
                background: var(--color-bg-secondary);
                border-radius: 12px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            
            .loading-animation {
                position: relative;
                width: 120px;
                height: 120px;
                margin-bottom: 2rem;
            }
            
            .loading-spinner-ring {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                border-radius: 50%;
                border: 3px solid transparent;
                border-top-color: var(--color-primary);
                animation: spin 1.5s linear infinite;
            }
            
            .loading-spinner-inner {
                position: absolute;
                top: 15px;
                left: 15px;
                right: 15px;
                bottom: 15px;
                border-radius: 50%;
                border: 3px solid transparent;
                border-top-color: var(--color-secondary);
                animation: spin 2s linear infinite reverse;
            }
            
            .loading-pulse {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 50%;
                height: 50%;
                background: radial-gradient(circle, var(--color-primary-light) 0%, transparent 70%);
                border-radius: 50%;
                opacity: 0.7;
                animation: pulse 2s ease-in-out infinite;
            }
            
            .particle-container {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
            }
            
            .particle {
                position: absolute;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: var(--color-primary);
                opacity: 0.7;
            }
            
            .particle-1 {
                top: 20%;
                left: 20%;
                animation: particleMove1 3s ease-in-out infinite;
            }
            
            .particle-2 {
                top: 20%;
                right: 20%;
                animation: particleMove2 3.5s ease-in-out infinite;
            }
            
            .particle-3 {
                bottom: 20%;
                left: 20%;
                animation: particleMove3 4s ease-in-out infinite;
            }
            
            .particle-4 {
                bottom: 20%;
                right: 20%;
                animation: particleMove4 3s ease-in-out infinite;
            }
            
            .loading-text {
                width: 100%;
                text-align: center;
            }
            
            .loading-title {
                margin-bottom: 1.5rem;
                font-size: 1.5rem;
                background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
                animation: titleGlow 2s ease-in-out infinite;
}

            .loading-steps {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
                margin-bottom: 1.5rem;
                width: 80%;
                margin: 0 auto 1.5rem;
            }
            
            .loading-step {
                padding: 0.5rem;
                border-radius: 4px;
                background: var(--color-bg-tertiary);
                opacity: 0.6;
                transition: all 0.3s ease;
                position: relative;
                padding-left: 1.5rem;
            }
            
            .loading-step:before {
                content: "";
                position: absolute;
                left: 0.5rem;
                top: 50%;
                transform: translateY(-50%);
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: var(--color-gray-400);
            }
            
            .loading-step.active {
                opacity: 1;
                background: var(--color-bg-primary);
                transform: translateX(5px);
                border-left: 3px solid var(--color-primary);
                font-weight: 500;
            }
            
            .loading-step.active:before {
                background: var(--color-primary);
            }
            
            .loading-step.completed:before {
                background: var(--color-success);
                content: "✓";
                font-size: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                line-height: 1;
            }
            
            .loading-message {
                font-size: 0.9rem;
                opacity: 0.8;
                max-width: 80%;
                margin: 0 auto;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            @keyframes pulse {
                0% { opacity: 0.4; transform: translate(-50%, -50%) scale(0.8); }
                50% { opacity: 0.7; transform: translate(-50%, -50%) scale(1.2); }
                100% { opacity: 0.4; transform: translate(-50%, -50%) scale(0.8); }
            }
            
            @keyframes particleMove1 {
                0%, 100% { transform: translate(0, 0); }
                50% { transform: translate(20px, 20px); }
            }
            
            @keyframes particleMove2 {
                0%, 100% { transform: translate(0, 0); }
                50% { transform: translate(-20px, 20px); }
}

            @keyframes particleMove3 {
                0%, 100% { transform: translate(0, 0); }
                50% { transform: translate(20px, -20px); }
            }
            
            @keyframes particleMove4 {
                0%, 100% { transform: translate(0, 0); }
                50% { transform: translate(-20px, -20px); }
            }
            
            @keyframes titleGlow {
                0%, 100% { opacity: 0.8; }
                50% { opacity: 1; }
            }
        `;
        document.head.appendChild(loadingStyles);
        
        // Animate the loading steps sequentially
        setTimeout(() => {
            const steps = loadingSection.querySelectorAll('.loading-step');
            let currentStep = 0;
            
            const animateNextStep = () => {
                if (currentStep > 0) {
                    steps[currentStep - 1].classList.add('completed');
                    steps[currentStep - 1].classList.remove('active');
                }
                
                if (currentStep < steps.length) {
                    steps[currentStep].classList.add('active');
                    currentStep++;
                    setTimeout(animateNextStep, 1500); // Time between step animations
                }
            };
            
            animateNextStep();
        }, 500); // Start after initial loading display
        
        // Scroll to loading section
        loadingSection.scrollIntoView({ behavior: 'smooth' });
        
        // Get form data
        const formData = new FormData(generateForm);
        
        // Create payload
        const payload = {
            topic: formData.get('topic'),
            tone: formData.get('tone'),
            expertise_level: formData.get('expertise_level'),
            variants: parseInt(formData.get('variants'))
        };
        
        // Add advanced options if visible
        const advancedOptions = document.getElementById('advanced-options');
        if (advancedOptions && !advancedOptions.classList.contains('hidden')) {
            // Use default values if parsing fails
            const maxLength = parseInt(formData.get('max_length')) || 1024;
            const tempValue = parseFloat(formData.get('temperature')) || 0.7;
            
            payload.max_length = maxLength;
            payload.temperature = tempValue;
        }
        
        // Log payload for debugging
        console.log("Sending request to /api/generate with payload:", payload);
            
        // Add error handling for the fetch request
        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });
            
            // Handle different error status codes
            if (!response.ok) {
                // Try to get error message from response
                let errorMessage = `Server responded with status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    if (errorData && errorData.error) {
                        errorMessage = errorData.error;
                    }
                } catch (parseError) {
                    console.error('Could not parse error response:', parseError);
                }
                
                throw new Error(errorMessage);
            }
            
            const result = await response.json();
            
            // Check if the result indicates success
            if (!result.success) {
                throw new Error(result.error || 'Server returned an unsuccessful response');
                }
                
            // Hide loading, show results
            loadingSection.classList.add('hidden');
            resultsSection.classList.remove('hidden');
                
            // Display results
            displayResults(result);
            
            // Scroll to results section
            resultsSection.scrollIntoView({ behavior: 'smooth' });
            
            // Reset button state
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.innerHTML = 'Generate <span class="icon-container"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-hover"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span>';
            }
            
        } catch (error) {
            console.error('Error generating content:', error);
                
            // Show error in loading section with more details
                loadingSection.innerHTML = `
                    <div class="error-container">
                    <h3>Error Generating Content</h3>
                    <p>${error.message || 'Something went wrong. Please try again.'}</p>
                    <div class="error-details">
                        <p>This might be due to:</p>
                        <ul>
                            <li>Server connectivity issues</li>
                            <li>API rate limits or temporary unavailability</li>
                            <li>Content policy restrictions on the requested topic</li>
                        </ul>
                    </div>
                    <button class="retry-button btn btn-primary" onclick="location.reload()">Try Again</button>
                    </div>
                `;
                
            // Style the error details
            const style = document.createElement('style');
            style.textContent = `
                .error-details {
                    margin-top: 1rem;
                    font-size: 0.9rem;
                    color: var(--color-gray-300);
                }
                .error-details ul {
                    margin-top: 0.5rem;
                    padding-left: 1.5rem;
                }
                .error-details li {
                    margin-bottom: 0.25rem;
                }
            `;
            document.head.appendChild(style);
            
            // Reset button state
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.innerHTML = 'Generate <span class="icon-container"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-hover"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span>';
            }
        }
    });
}

/**
 * Display results returned from the API
 */
function displayResults(result) {
    console.log('Displaying results for topic:', result.topic);
    
    try {
        // Set topic heading
        const topicHeading = document.getElementById('topic-heading');
        if (topicHeading) {
            topicHeading.textContent = result.topic;
        }
        
        // Get expertise level from result
        const expertiseLevel = result.expertise_level || 'intermediate';
        console.log(`Using expertise level: ${expertiseLevel}`);
        
        // Track the detected tone to ensure visual consistency
        let detectedTone = 'informative'; // Default tone
        
        // Process result.result if it exists (this is the full result object)
        const fullResult = result.result || {};
        
        // Display narrative first to determine the tone
        if (result.narrative || (fullResult && fullResult.narrative)) {
            // Use either direct narrative or from fullResult
            const narrativeData = result.narrative || (fullResult && fullResult.narrative) || null;
            if (narrativeData) {
                displayNarrative(narrativeData, expertiseLevel);
            
            // Extract tone from narrative container for consistency
            const narrativeContainer = document.querySelector('.narrative-container');
            if (narrativeContainer) {
                const toneClass = Array.from(narrativeContainer.classList)
                    .find(cls => cls.startsWith('tone-'));
                
                if (toneClass) {
                    detectedTone = toneClass.replace('tone-', '');
                    console.log(`Detected narrative tone: ${detectedTone}`);
                    }
                }
            }
        } else {
            console.warn('No narrative data available');
            const narrativeContainer = document.querySelector('.narrative-container');
            if (narrativeContainer) {
                narrativeContainer.innerHTML = `
                    <h2 id="topic-heading">${result.topic || 'Unknown Topic'}</h2>
                    <div class="error-container">
                        <h3>Narrative Generation Error</h3>
                        <p>We couldn't generate a narrative for this topic. Please try again with a different topic or tone.</p>
                    </div>
                `;
            }
        }
        
        // Display images with matching tone
        const images = result.images || (fullResult && fullResult.images) || [];
        if (images && images.length > 0) {
            displayImages(images);
        } else {
            console.warn('No image data available');
            const imagesContainer = document.getElementById('images-container');
            if (imagesContainer) {
                imagesContainer.innerHTML = `
                    <div class="error-container">
                        <h3>No Images Available</h3>
                        <p>We couldn't generate images for this topic. Image generation may be temporarily unavailable.</p>
                    </div>
                `;
            }
        }
        
        // Check if visualizations are available and handle tab visibility
        const visualizations = result.visualizations || (fullResult && fullResult.visualizations) || null;
        if (visualizations) {
            // Always show the visualization tab
            showVisualizationTab();
            
            // Store visualization data for later initialization
            // Instead of immediately displaying visualizations, store the data as an attribute
            const vizContainer = document.querySelector('.viz-container');
            if (vizContainer) {
                // Store visualization data as a data attribute
                vizContainer.setAttribute('data-viz-available', 'true');
                // Store the actual data as a JSON string in a hidden input
                let vizDataInput = document.getElementById('visualization-data');
                if (!vizDataInput) {
                    vizDataInput = document.createElement('input');
                    vizDataInput.type = 'hidden';
                    vizDataInput.id = 'visualization-data';
                    document.body.appendChild(vizDataInput);
                }
                // Store the visualization data for later use
                vizDataInput.value = JSON.stringify(visualizations);
            }
        } else {
            console.warn('No visualization data available');
            // Still show the tab, but prepare it for default visualizations
            showVisualizationTab();
            // Mark that we have no visualization data
            const vizContainer = document.querySelector('.viz-container');
            if (vizContainer) {
                vizContainer.setAttribute('data-viz-available', 'false');
            }
        }
        
        // Display data sources
        const data = result.data || (fullResult && fullResult.data) || null;
        if (data) {
            displayDataSources(data);
        } else {
            console.warn('No source data available');
            const dataSourcesContainer = document.querySelector('.data-sources');
            if (dataSourcesContainer) {
                dataSourcesContainer.innerHTML = `
                    <div class="error-container">
                        <h3>No Source Data Available</h3>
                        <p>We couldn't retrieve source data for this topic. Data sources may be temporarily unavailable.</p>
                    </div>
                `;
            }
        }
        
        // Set the topic for the conversation
        const conversationTopic = document.getElementById('conversation-topic');
        if (conversationTopic) {
            conversationTopic.textContent = result.topic || 'this topic';
        }
        
        // Initialize conversation interface
        setupConversation();
        
        // Display success message
        console.log("Results displayed successfully");
    } catch (error) {
        console.error('Error displaying results:', error);
        const resultsSection = document.getElementById('results');
        if (resultsSection) {
            resultsSection.innerHTML = `
                <div class="error-container">
                    <h3>Error Displaying Results</h3>
                    <p>${error.message || 'An unknown error occurred while displaying results.'}</p>
                    <button class="retry-button btn btn-primary" onclick="location.reload()">Try Again</button>
                </div>
            `;
        }
    }
}

/**
 * Check if the visualization data has valid content to display
 */
function hasValidVisualizationData(visualizations) {
    if (!visualizations) return false;
    if (visualizations.error) return false;
    
    // Check for timeline data
    const hasTimeline = visualizations.timeline && 
                        visualizations.timeline.data && 
                        Array.isArray(visualizations.timeline.data) && 
                        visualizations.timeline.data.length > 0;
    
    // Check for category bar data
    const hasCategoryBar = visualizations.category_bar && 
                          visualizations.category_bar.data && 
                          Array.isArray(visualizations.category_bar.data) && 
                          visualizations.category_bar.data.length > 0;
    
    // Check for concept map data
    const hasConceptMap = visualizations.concept_map && 
                         visualizations.concept_map.nodes && 
                         visualizations.concept_map.links && 
                         Array.isArray(visualizations.concept_map.nodes) && 
                         visualizations.concept_map.nodes.length > 0;
    
    // Return true if at least one visualization type has valid data
    return hasTimeline || hasCategoryBar || hasConceptMap;
}

/**
 * Hide the visualization tab and adjust other tabs
 */
function hideVisualizationTab() {
    // Find the visualization tab link
    const vizTabLink = document.querySelector('.tab-link[data-tab="visualizations"]');
    if (vizTabLink) {
        // Get the parent li element
        const vizTabLi = vizTabLink.parentElement;
        if (vizTabLi) {
            // Hide the tab
            vizTabLi.style.display = 'none';
            
            // If the visualization tab is currently active, activate the narrative tab instead
            if (vizTabLink.classList.contains('active')) {
                // Use the new activateTab method to switch to the narrative tab
                window.activateTab("narrative");
            }
            
            console.log('Visualization tab hidden');
        }
    }
}

/**
 * Show the visualization tab if it was previously hidden
 */
function showVisualizationTab() {
    // Find the visualization tab link
    const vizTabLink = document.querySelector('.tab-link[data-tab="visualizations"]');
    if (vizTabLink) {
        // Get the parent li element
        const vizTabLi = vizTabLink.parentElement;
        if (vizTabLi) {
            // Make sure the tab is visible
            vizTabLi.style.display = '';
            console.log('Visualization tab shown');
        }
    }
}

/**
 * Display data visualizations
 * Returns true if at least one visualization was successfully displayed
 */
function displayVisualizations(visualizations) {
    console.log('Visualization data received:', visualizations);
    
    // Track if any visualization was actually displayed
    let hasDisplayedVisualizations = false;
    
    if (!visualizations) {
        console.warn('No visualization data provided');
        document.querySelectorAll('.viz-panel').forEach(panel => {
            panel.innerHTML = '<p>No visualization data available.</p>';
        });
        return false;
    }
    
    // Check if there was an error in generating visualizations
    if (visualizations.error) {
        console.error('Visualization error:', visualizations.error);
        document.querySelectorAll('.viz-panel').forEach(panel => {
            panel.innerHTML = `<p>Error generating visualizations: ${visualizations.error}</p>`;
        });
        return false;
    }
    
    // Timeline visualization
    try {
        const timelineDiv = document.getElementById('timeline-viz');
        if (timelineDiv) {
            console.log('Timeline data:', visualizations.timeline);
            if (visualizations.timeline && visualizations.timeline.data && visualizations.timeline.layout) {
                if (Array.isArray(visualizations.timeline.data) && visualizations.timeline.data.length > 0) {
                    console.log('Creating timeline with data:', visualizations.timeline.data);
                    
                    Plotly.newPlot(timelineDiv, visualizations.timeline.data, visualizations.timeline.layout)
                        .then(() => {
                            console.log('Timeline plotted successfully');
                            hasDisplayedVisualizations = true;
                        })
                        .catch(err => {
                            console.error('Plotly timeline error:', err);
                            timelineDiv.innerHTML = `<p>Could not display timeline visualization: ${err.message}</p>`;
                        });
                } else {
                    console.error('Timeline data empty or not an array');
                    timelineDiv.innerHTML = '<p>Timeline data is empty or malformed.</p>';
                }
            } else {
                timelineDiv.innerHTML = '<p>No timeline data available for this topic.</p>';
            }
        }
    } catch (error) {
        console.error('Error creating timeline visualization:', error);
        const timelineDiv = document.getElementById('timeline-viz');
        if (timelineDiv) {
            timelineDiv.innerHTML = `<p>Error displaying timeline: ${error.message}</p>`;
        }
    }
    
    // Category bar chart
    try {
        const categoryDiv = document.getElementById('category-viz');
        if (categoryDiv) {
            console.log('Category data:', visualizations.category_bar);
            if (visualizations.category_bar && visualizations.category_bar.data && visualizations.category_bar.layout) {
                if (Array.isArray(visualizations.category_bar.data) && visualizations.category_bar.data.length > 0) {
                    console.log('Creating category bar with data:', visualizations.category_bar.data);
                    
                    Plotly.newPlot(categoryDiv, visualizations.category_bar.data, visualizations.category_bar.layout)
                        .then(() => {
                            console.log('Category bar plotted successfully');
                            hasDisplayedVisualizations = true;
                        })
                        .catch(err => {
                            console.error('Plotly category bar error:', err);
                            categoryDiv.innerHTML = `<p>Could not display category visualization: ${err.message}</p>`;
                        });
                } else {
                    console.error('Category data empty or not an array');
                    categoryDiv.innerHTML = '<p>Category data is empty or malformed.</p>';
                }
            } else {
                categoryDiv.innerHTML = '<p>No category data available for this topic.</p>';
            }
        }
    } catch (error) {
        console.error('Error creating category visualization:', error);
        const categoryDiv = document.getElementById('category-viz');
        if (categoryDiv) {
            categoryDiv.innerHTML = `<p>Error displaying categories: ${error.message}</p>`;
        }
    }
    
    // Concept map - Using D3.js
    try {
        const conceptDiv = document.getElementById('concept-viz');
        if (conceptDiv) {
            console.log('Concept map data:', visualizations.concept_map);
            if (visualizations.concept_map && visualizations.concept_map.nodes && visualizations.concept_map.links) {
                if (Array.isArray(visualizations.concept_map.nodes) && 
                    Array.isArray(visualizations.concept_map.links) &&
                    visualizations.concept_map.nodes.length > 0) {
                    
                    console.log('Creating concept map with nodes:', visualizations.concept_map.nodes);
                    renderConceptMap(conceptDiv, visualizations.concept_map);
                    console.log('Concept map rendered successfully');
                    hasDisplayedVisualizations = true;
                } else {
                    console.error('Concept map nodes/links are empty or not arrays');
                    conceptDiv.innerHTML = '<p>Concept map data is empty or malformed.</p>';
                }
            } else {
                conceptDiv.innerHTML = '<p>No concept map data available for this topic.</p>';
            }
        }
    } catch (error) {
        console.error('Error creating concept map:', error);
        const conceptDiv = document.getElementById('concept-viz');
        if (conceptDiv) {
            conceptDiv.innerHTML = `<p>Error displaying concept map: ${error.message}</p>`;
        }
    }
    
    // Return whether any visualization was displayed successfully
    return hasDisplayedVisualizations;
}

/**
 * Render a concept map using D3.js
 */
function renderConceptMap(container, data) {
    if (!data || !data.nodes || !data.links || data.nodes.length === 0) {
        container.innerHTML = '<p>No concept map data available.</p>';
        return;
    }
    
    container.innerHTML = `<h3>${data.title || 'Concept Map'}</h3>`;
    
    // Set up D3 force simulation
    const width = container.clientWidth;
    const height = 300;
    
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);
        
    // Add group for zoom/pan
    const g = svg.append('g');
    
    // Color scale for node groups
    const color = d3.scaleOrdinal(d3.schemeCategory10);
    
    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2));
    
    // Draw links
    const link = g.append('g')
        .selectAll('line')
        .data(data.links)
        .enter().append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', d => Math.sqrt(d.value));
    
    // Draw nodes
    const node = g.append('g')
        .selectAll('circle')
        .data(data.nodes)
        .enter().append('circle')
        .attr('r', d => d.group === 1 ? 10 : 7)
        .attr('fill', d => color(d.group))
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    // Add labels
    const labels = g.append('g')
        .selectAll('text')
        .data(data.nodes)
        .enter().append('text')
        .text(d => d.id)
        .attr('font-size', d => d.group === 1 ? '12px' : '10px')
        .attr('dx', 12)
        .attr('dy', 4)
        .style('fill', '#f0f0f0');
    
    // Update positions on each tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        labels
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });
    
    // Drag functions
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

/**
 * Display narrative content with enhanced, tone-specific formatting
 */
function displayNarrative(narrative, expertiseLevel = 'intermediate') {
    const bulletsContainer = document.getElementById('bullets-container');
    const narrativeText = document.getElementById('narrative-text');
    const topicHeading = document.getElementById('topic-heading');
    
    if (!bulletsContainer || !narrativeText) {
        console.error("Narrative containers not found");
        return;
    }
    
    console.log('Displaying narrative:', narrative);
    
    // Clear previous content
    bulletsContainer.innerHTML = '';
    narrativeText.innerHTML = '';
    
    // Extract narrative tone from the prompt (if available)
    let tone = 'informative'; // Default tone
    if (narrative.prompt) {
        const toneMatch = narrative.prompt.match(/Write a (\w+) narrative about/i);
        if (toneMatch && toneMatch[1]) {
            tone = toneMatch[1].toLowerCase();
        }
    }
    
    console.log(`Detected narrative tone: ${tone}`);
    
    // Get expertise level from the narrative object or use the parameter
    const level = narrative.expertise_level || expertiseLevel || 'intermediate';
    console.log(`Using expertise level: ${level}`);
    
    // Apply tone-specific container styling
    const narrativeContainer = document.querySelector('.narrative-container');
    
    // Reset any previously applied classes
    narrativeContainer.className = 'narrative-container';
    narrativeContainer.classList.add(`tone-${tone}`);
    narrativeContainer.classList.add(`expertise-${level}`);
    
    // Format bullet points based on tone
    if (narrative.bullets) {
        formatBulletsByTone(bulletsContainer, narrative.bullets, tone);
    } else {
        bulletsContainer.classList.add('hidden');
    }
    
    // Format narrative text with tone-specific styling
    if (narrative.narrative) {
        formatNarrativeByTone(narrativeText, narrative.narrative, tone, topicHeading.textContent);
    } else {
        narrativeText.innerHTML = '<p>No narrative content available.</p>';
    }
}

/**
 * Format bullet points based on narrative tone
 */
function formatBulletsByTone(container, bullets, tone) {
    // Clear any previous content
    container.innerHTML = '';
    container.classList.remove('hidden');
    
    // Split bullets into array
    const bulletPoints = bullets.split('\n').filter(b => b.trim().length > 0);
    
    switch(tone) {
        case 'dramatic':
            // Create dramatic, bold bullets with fading effects
            container.classList.add('dramatic-bullets');
            
            bulletPoints.forEach((bullet, index) => {
                const bulletEl = document.createElement('div');
                bulletEl.className = 'dramatic-bullet';
                bulletEl.style.animationDelay = `${index * 0.2}s`;
                
                // Bold the first part of each bullet for emphasis
                const parts = bullet.split(' ');
                const firstPart = parts.slice(0, 2).join(' ');
                const restPart = parts.slice(2).join(' ');
                
                bulletEl.innerHTML = `<strong>${firstPart}</strong> ${restPart}`;
                container.appendChild(bulletEl);
            });
            break;
            
        case 'poetic':
            // Create flowing, italic bullets with a softer aesthetic
            container.classList.add('poetic-bullets');
            
            // Create a decorative wrapper
            const poeticWrapper = document.createElement('div');
            poeticWrapper.className = 'poetic-bullets-wrapper';
            
            bulletPoints.forEach(bullet => {
                const bulletEl = document.createElement('p');
                bulletEl.className = 'poetic-bullet';
                
                // Replace the bullet marker with a more poetic symbol
                bullet = bullet.replace(/^[•\*\-]\s+/, '');
                bulletEl.innerHTML = `<span class="poetic-symbol">❋</span> <em>${bullet}</em>`;
                poeticWrapper.appendChild(bulletEl);
            });
            
            container.appendChild(poeticWrapper);
            break;
            
        case 'humorous':
            // Create playful, colorful bullets with quirky icons
            container.classList.add('humorous-bullets');
            
            const icons = ['😀', '🤣', '😎', '🤪', '👍', '🎭', '🎪', '🎯'];
            
            bulletPoints.forEach((bullet, index) => {
                const bulletEl = document.createElement('div');
                bulletEl.className = 'humorous-bullet';
                
                // Use a rotating set of emoji icons
                const icon = icons[index % icons.length];
                
                // Replace the bullet marker with the emoji
                bullet = bullet.replace(/^[•\*\-]\s+/, '');
                bulletEl.innerHTML = `<span class="humorous-icon">${icon}</span> ${bullet}`;
                container.appendChild(bulletEl);
            });
            break;
            
        case 'technical':
            // Create structured, code-like bullets
            container.classList.add('technical-bullets');
            
            // Create a code-block style container
            const techWrapper = document.createElement('div');
            techWrapper.className = 'technical-bullets-wrapper';
            
            // Add a "terminal" header
            const header = document.createElement('div');
            header.className = 'technical-header';
            header.innerHTML = '<span>●</span><span>●</span><span>●</span> key_points.md';
            techWrapper.appendChild(header);
            
            const techContent = document.createElement('div');
            techContent.className = 'technical-content';
            
            bulletPoints.forEach((bullet, index) => {
                const bulletEl = document.createElement('pre');
                bulletEl.className = 'technical-bullet';
                
                // Replace the bullet marker with numbering
                bullet = bullet.replace(/^[•\*\-]\s+/, '');
                bulletEl.innerHTML = `<span class="line-number">${index + 1}.</span> <span class="code-keyword">const</span> point_${index + 1} = <span class="code-string">"${bullet}"</span>;`;
                techContent.appendChild(bulletEl);
            });
            
            techWrapper.appendChild(techContent);
            container.appendChild(techWrapper);
            break;
            
        case 'simple':
            // Create clean, minimalist bullets with plenty of whitespace
            container.classList.add('simple-bullets');
            
            bulletPoints.forEach(bullet => {
                const bulletEl = document.createElement('div');
                bulletEl.className = 'simple-bullet';
                
                // Clean and simplify the bullet text
                bullet = bullet.replace(/^[•\*\-]\s+/, '');
                bulletEl.textContent = bullet;
                container.appendChild(bulletEl);
            });
            break;
            
        default: // informative or any other type
            // Standard bullet points with a clean, academic style
            container.classList.add('informative-bullets');
            
            const bulletList = document.createElement('ul');
            bulletList.className = 'informative-bullet-list';
            
            bulletPoints.forEach(bullet => {
                const bulletEl = document.createElement('li');
                
                // Clean up the bullet text
                bullet = bullet.replace(/^[•\*\-]\s+/, '');
                bulletEl.innerHTML = bullet;
                bulletList.appendChild(bulletEl);
            });
            
            container.appendChild(bulletList);
            break;
    }
}

/**
 * Format narrative text based on tone
 */
function formatNarrativeByTone(container, narrativeText, tone, topic) {
    // Clear previous content
    container.innerHTML = '';
    
    // Split into paragraphs
    const paragraphs = narrativeText.split('\n\n').filter(p => p.trim().length > 0);
    
    switch(tone) {
        case 'dramatic':
            // Create a cinematic, dramatic layout with big quotes and emphasis
            container.classList.add('dramatic-narrative');
            
            // Add a dramatic quote to start
            const quoteDiv = document.createElement('div');
            quoteDiv.className = 'dramatic-quote';
            
            // Extract a powerful sentence from the first paragraph for the quote
            const firstPara = paragraphs[0];
            const sentences = firstPara.split(/(?<=[.!?])\s+/);
            let quoteSentence = sentences[0];
            // Try to find a more interesting sentence if the first one is short
            if (sentences.length > 1 && sentences[0].length < 50) {
                quoteSentence = sentences.find(s => s.length > 50) || sentences[1];
            }
            
            quoteDiv.innerHTML = `<span class="quote-mark">"</span>${quoteSentence}<span class="quote-mark">"`;
            container.appendChild(quoteDiv);
            
            // Add the rest of the content with dramatic styling
            paragraphs.forEach((para, index) => {
                const paraDiv = document.createElement('div');
                paraDiv.className = 'dramatic-paragraph';
                
                // Skip the sentence we used for the quote if it's the first paragraph
                if (index === 0) {
                    paraDiv.innerHTML = para.replace(quoteSentence, '');
                } else {
                    // For the last paragraph, add extra dramatic conclusion styling
                    if (index === paragraphs.length - 1) {
                        paraDiv.classList.add('dramatic-conclusion');
                    }
                    paraDiv.innerHTML = para;
                }
                container.appendChild(paraDiv);
            });
            break;
            
        case 'poetic':
            // Create a flowing, artistic layout with line breaks and calligraphic styling
            container.classList.add('poetic-narrative');
            
            // Check if the narrative has line breaks within paragraphs (enhanced poetic structure)
            const hasPoetryLineBreaks = paragraphs.some(p => p.includes('\n'));
            
            // Create a poem-like structure
            let poemHTML = '';
            
            // Special poetic intro
            poemHTML += `<div class="poem-title">${topic}</div>`;
            
            // Add a decorative initial letter for poetry
            poemHTML += `<div class="poem-decorative-container">
                <div class="poem-decorative-letter">${paragraphs[0].charAt(0)}</div>`;
            
            // Process each paragraph as a stanza, with special handling for line breaks
            if (hasPoetryLineBreaks) {
                // Handle enhanced poetic format with pre-inserted line breaks
                paragraphs.forEach((para, index) => {
                    // Split into poetic lines if there are line breaks
                    const poeticLines = para.split('\n');
                    
                    const stanzaClass = index === 0 ? 'poem-stanza first-stanza' : 'poem-stanza';
                    poemHTML += `<div class="${stanzaClass}">`;
                    
                    poeticLines.forEach((line, lineIndex) => {
                        // For the first line of first paragraph, skip the first character (already used in decorative letter)
                        if (index === 0 && lineIndex === 0) {
                            line = line.substring(1); // Skip the first character
                        }
                        
                        // Add each line with poetic styling
                        if (line.trim()) {
                            poemHTML += `<p class="poetic-line">${line}</p>`;
                        }
                    });
                    
                    poemHTML += `</div>`;
                    
                    // Add decorative separator between stanzas
                    if (index < paragraphs.length - 1) {
                        poemHTML += `<div class="poem-separator">❦</div>`;
                    }
                });
            } else {
                // Standard paragraphs - convert to poetic stanzas
                paragraphs.forEach((para, index) => {
                    // Split into sentences for poetic effect
                    const sentences = para.split(/(?<=[.!?])\s+/);
                    const stanzaClass = index === 0 ? 'poem-stanza first-stanza' : 'poem-stanza';
                    
                    poemHTML += `<div class="${stanzaClass}">`;
                    
                    // Process each sentence as a poetic line
                    sentences.forEach((sentence, sentIndex) => {
                        // For first sentence of first paragraph, skip the first character (decorative)
                        if (index === 0 && sentIndex === 0) {
                            sentence = sentence.substring(1); // Skip the first character
                        }
                        
                        // Add each sentence as a poetic line
                        if (sentence.trim()) {
                            poemHTML += `<p class="poetic-line">${sentence}</p>`;
                        }
                    });
                    
                    poemHTML += `</div>`;
                    
                    // Add decorative separator between stanzas
                    if (index < paragraphs.length - 1) {
                        poemHTML += `<div class="poem-separator">❦</div>`;
                    }
                });
            }
            
            // Close the decorative container
            poemHTML += `</div>`;
            
            // Add a poetic closing flourish
            poemHTML += `<div class="poem-footer">✧ ✧ ✧</div>`;
            
            container.innerHTML = poemHTML;
            
            // Add dynamic text animation for the poetic lines
            setTimeout(() => {
                const poeticLines = container.querySelectorAll('.poetic-line');
                poeticLines.forEach((line, i) => {
                    line.style.animationDelay = `${i * 0.1}s`;
                    line.classList.add('animate-in');
                });
            }, 100);
            
            break;
            
        case 'humorous':
            // Create a fun, playful layout with comic-like elements
            container.classList.add('humorous-narrative');
            
            // Check for current cultural references in the text
            const hasCurrentReferences = narrativeText.toLowerCase().includes('trending') || 
                                         narrativeText.toLowerCase().includes('tiktok') || 
                                         /20(2[3-9]|3\d)/.test(narrativeText); // Match years 2023-2039
            
            let humorHTML = '';
            
            // Add a fun title with emoji
            humorHTML += `<div class="humor-title">😂 The ${hasCurrentReferences ? 'Totally Hip' : 'Not-So-Serious'} Guide to ${topic} 🎭</div>`;
            
            // Add fun "comedy special" banner if there are pop culture references
            if (hasCurrentReferences) {
                const currentYear = new Date().getFullYear();
                humorHTML += `<div class="humor-banner">
                    <span class="humor-banner-text">LIVE FROM THE INTERNET ${currentYear}</span>
                    <span class="humor-banner-emoji">🎬</span>
                </div>`;
            }
            
            // Add comic-like sections
            paragraphs.forEach((para, index) => {
                // Random funny emojis to sprinkle through the text
                const funnyEmojis = ['😂', '🤣', '😎', '🤪', '👍', '🎭', '🎪', '😄', '🙃', '🎯', '👑', '🎮', '🦄', '👽', '🍕'];
                const randomEmoji = funnyEmojis[Math.floor(Math.random() * funnyEmojis.length)];
                
                // Different container styles for variety
                let paraClass = index % 2 === 0 ? 'humor-paragraph' : 'humor-paragraph alt';
                
                // Special styling for intro and conclusion
                if (index === 0) {
                    paraClass = 'humor-intro';
                } else if (index === paragraphs.length - 1) {
                    paraClass = 'humor-punchline';
                }
                
                // Check if the paragraph contains a comparison (likely a joke)
                const hasComparison = para.includes(' like ') || para.includes(' as ') || para.includes('—');
                
                // Add speech bubble-like containers
                humorHTML += `
                    <div class="${paraClass}">
                        <span class="humor-emoji">${randomEmoji}</span>
                        <div class="humor-text ${hasComparison ? 'has-joke' : ''}">
                            ${para.replace(/\*([^*]+)\*/g, '<span class="humor-emphasis">$1</span>')}
                        </div>
                        ${hasComparison ? '<div class="joke-indicator">BA DUM TSS 🥁</div>' : ''}
                    </div>
                `;
                
                // Add a meme-style image placeholder for one of the middle paragraphs
                if (index === Math.floor(paragraphs.length / 2) && paragraphs.length > 2) {
                    humorHTML += `
                        <div class="humor-meme">
                            <div class="meme-caption">How people look when they learn about ${topic}</div>
                            <div class="meme-frame">
                                <div class="meme-image">🤯</div>
                            </div>
                            <div class="meme-caption">Mind = Blown</div>
                        </div>
                    `;
                }
            });
            
            // Add a humorous footer with a "like and subscribe" parody
            humorHTML += `
                <div class="humor-footer">
                    <div class="humor-tagline">If you laughed, you learned! If you didn't laugh, pretend you did! 🎓</div>
                    <div class="humor-subscribe">Don't forget to like, subscribe, and turn on notifications for more ${topic} facts! 
                    <span class="humor-small">(Just kidding, that's not how books work)</span></div>
                </div>`;
            
            container.innerHTML = humorHTML;
            
            // Add some dynamic effects for humor elements
            setTimeout(() => {
                // Make emojis bounce
                const emojis = container.querySelectorAll('.humor-emoji');
                emojis.forEach((emoji, i) => {
                    emoji.style.animationDelay = `${i * 0.2}s`;
                    emoji.classList.add('bounce');
                });
                
                // Add hover effects to joke indicators
                const jokes = container.querySelectorAll('.joke-indicator');
                jokes.forEach(joke => {
                    joke.addEventListener('mouseenter', () => {
                        joke.textContent = 'THAT WAS A JOKE! 🎯';
                    });
                    joke.addEventListener('mouseleave', () => {
                        joke.textContent = 'BA DUM TSS 🥁';
                    });
                });
            }, 100);
            
            break;
            
        case 'technical':
            // Create a documentation-like layout with code blocks and technical styling
            container.classList.add('technical-narrative');
            
            let techHTML = `<div class="tech-header"># Documentation: ${topic}</div>`;
            
            // Add sections with code-like formatting
            paragraphs.forEach((para, index) => {
                // Check if paragraph starts with a header marker from enhanced text
                const hasHeader = para.startsWith('##') || para.startsWith('OVERVIEW:') || para.startsWith('SUMMARY:');
                
                if (hasHeader) {
                    // Extract header text
                    let headerText = para;
                    let contentText = '';
                    
                    if (para.startsWith('##')) {
                        const headerParts = para.split('\n');
                        headerText = headerParts[0].replace('##', '').trim();
                        contentText = headerParts.slice(1).join('\n');
                    } else if (para.startsWith('OVERVIEW:')) {
                        headerText = 'Overview';
                        contentText = para.replace('OVERVIEW:', '').trim();
                    } else if (para.startsWith('SUMMARY:')) {
                        headerText = 'Summary';
                        contentText = para.replace('SUMMARY:', '').trim();
                    }
                    
                    techHTML += `<div class="tech-section">
                        <div class="tech-section-title">## ${headerText}</div>
                        <div class="tech-content">${contentText}</div>
                    </div>`;
                } else if (index === 0) {
                    // First paragraph as overview if no header
                    techHTML += `<div class="tech-overview">
                        <div class="tech-section-title">## Overview</div>
                        <div class="tech-content">${para}</div>
                    </div>`;
                } else {
                    // Generate section titles based on paragraph content
                    const sectionTitles = ['Details', 'Implementation', 'Architecture', 'Specifications', 'Analysis'];
                    const sectionTitle = sectionTitles[Math.min(index-1, sectionTitles.length-1)];
                    
                    techHTML += `<div class="tech-section">
                        <div class="tech-section-title">## ${sectionTitle}</div>
                        <div class="tech-content">${para}</div>
                    </div>`;
                    
                    // Add a code snippet example for one of the middle paragraphs
                    if (index === Math.ceil(paragraphs.length / 2)) {
                        techHTML += `<div class="tech-code-block">
                            <div class="code-header">
                                <span>●</span><span>●</span><span>●</span> 
                                <span class="filename">example_code.js</span>
                            </div>
                            <pre>
/**
 * ${topic} implementation
 * This is a pseudocode representation
 */
function process${topic.replace(/\s+/g, '')}(data) {
  // Initialize the system
  const system = new ${topic.replace(/\s+/g, '')}System();
  
  // Process the data
  const result = system.analyze(data);
  
  return result;
}</pre>
                        </div>`;
                    }
                }
            });
            
            container.innerHTML = techHTML;
            break;
            
        case 'simple':
            // Create a clean, minimal layout with excellent readability
            container.classList.add('simple-narrative');
            
            // Simple header
            let simpleHTML = `<div class="simple-title">${topic}</div>`;
            
            // Clearly separated paragraphs with minimal styling
            paragraphs.forEach((para, index) => {
                let paraClass = 'simple-paragraph';
                
                // First paragraph gets a simple introduction style
                if (index === 0) {
                    paraClass += ' simple-intro';
                    
                    // Add a first-letter effect but very minimal
                    const firstChar = para.charAt(0);
                    const restOfText = para.substring(1);
                    para = `<span class="simple-first-letter">${firstChar}</span>${restOfText}`;
                }
                
                simpleHTML += `<p class="${paraClass}">${para}</p>`;
                
                // Add divider dots between paragraphs, but not after the last one
                if (index < paragraphs.length - 1) {
                    simpleHTML += `<div class="simple-divider">·&nbsp;·&nbsp;·</div>`;
                }
            });
            
            container.innerHTML = simpleHTML;
            break;
            
        default: // informative or any other tone
            // Create a scholarly, academic layout with sections and references
            container.classList.add('informative-narrative');
            
            // Check if paragraphs have headers
            const hasHeaders = paragraphs.some(p => p.startsWith('##'));
            
            let infoHTML = `<div class="info-header">${topic}</div>`;
            
            if (hasHeaders) {
                // Process paragraphs with headers
                infoHTML += `<div class="info-content">`;
                
                paragraphs.forEach((para, index) => {
                    if (para.startsWith('##')) {
                        // Split header and content
                        const parts = para.split('\n');
                        const header = parts[0].replace('##', '').trim();
                        const content = parts.slice(1).join('\n');
                        
                        infoHTML += `
                            <div class="info-section">
                                <div class="info-section-title">${header}</div>
                                <p>${content}</p>
                            </div>
                        `;
                    } else {
                        // Regular paragraph
                        infoHTML += `
                            <div class="info-section">
                                <p>${para}</p>
                            </div>
                        `;
                    }
                });
                
                infoHTML += `</div>`;
            } else {
                // Create article-like structure
                infoHTML += `<div class="info-abstract">
                    <div class="info-section-title">Abstract</div>
                    <p>${paragraphs[0]}</p>
                </div>`;
                
                // Create informative sections with scholarly styling
                const remainder = paragraphs.slice(1);
                
                // If we have multiple paragraphs, organize them into sections
                if (remainder.length > 0) {
                    infoHTML += `<div class="info-content">`;
                    
                    // Create sections from the remaining paragraphs
                    const sections = ['Introduction', 'Background', 'Analysis', 'Discussion', 'Conclusion'];
                    
                    remainder.forEach((para, index) => {
                        // Get an appropriate section title based on index
                        const sectionTitle = index < sections.length ? 
                            sections[index] : `Section ${index + 1}`;
                        
                        infoHTML += `
                            <div class="info-section">
                                <div class="info-section-title">${sectionTitle}</div>
                                <p>${para}</p>
                            </div>
                        `;
                    });
                    
                    infoHTML += `</div>`;
                }
            }
            
            container.innerHTML = infoHTML;
            break;
    }
}

/**
 * Display images returned from the API with tone-specific styling
 */
function displayImages(images) {
    const imagesContainer = document.getElementById('images-container');
    const imagePrompt = document.getElementById('image-prompt');
    
    if (!images || images.length === 0) {
        console.warn('No images to display');
        const noImagesMessage = document.createElement('p');
        noImagesMessage.className = `${tone}-no-images`;
        
        switch(tone) {
            case 'dramatic':
                noImagesMessage.innerHTML = "No visual elements available for this narrative.";
                break;
            case 'poetic':
                noImagesMessage.innerHTML = "The canvas remains blank, awaiting inspiration.";
                break;
            case 'humorous':
                noImagesMessage.innerHTML = "Looks like the artist took the day off! 🏖️";
                break;
            case 'technical':
                noImagesMessage.innerHTML = "ERROR: No image assets found in response data.";
                break;
            default:
                noImagesMessage.innerHTML = "No images were generated.";
        }
        
        imagesContainer.appendChild(noImagesMessage);
        return;
    }
    
    // Process each image
    images.forEach((image, index) => {
        console.log(`Processing image ${index}:`, image);
        
        // Create the image card container with tone-specific class
        const imageCard = document.createElement('div');
        imageCard.className = `image-card ${tone}-image-card`;
        
        if (tone === 'dramatic') {
            // Add animation delay for staggered effect
            imageCard.style.animationDelay = `${index * 0.2}s`;
        }
        
        // Show loading indicator while image loads
        const loadingDiv = document.createElement('div');
        loadingDiv.className = `loading-indicator ${tone}-loading`;
        loadingDiv.textContent = tone === 'technical' ? 'Loading asset...' : 'Loading image...';
        imageCard.appendChild(loadingDiv);
        
        // Check if image has a valid URL
        let imgUrl = image.url;
        
        // If URL doesn't start with a slash or http, add a leading slash
        if (imgUrl && !imgUrl.startsWith('/') && !imgUrl.startsWith('http')) {
            imgUrl = '/' + imgUrl;
            console.log(`Fixed image URL to: ${imgUrl}`);
        }
        
        if (imgUrl) {
            const imgWrapper = document.createElement('div');
            imgWrapper.className = `image-wrapper ${tone}-image-wrapper`;
            
            const img = document.createElement('img');
            img.src = imgUrl;
            img.alt = `Generated image ${index + 1}`;
            img.className = `${tone}-image`;
            img.style.width = '100%';
            img.style.height = 'auto';
            
            img.onload = () => {
                loadingDiv.remove();
            };
            
            img.onerror = () => {
                console.error(`Failed to load image: ${imgUrl}`);
                loadingDiv.textContent = 'Failed to load image';
                loadingDiv.className = `loading-indicator ${tone}-loading error`;
            };
            
            imgWrapper.appendChild(img);
            imageCard.appendChild(imgWrapper);
            
            // Add image info
            const infoDiv = document.createElement('div');
            infoDiv.className = `image-info ${tone}-image-info`;
            
            switch(tone) {
                case 'dramatic':
                    infoDiv.innerHTML = `
                        <h4>Perspective ${index + 1}</h4>
                        <p class="dramatic-image-style">${image.style || 'Style unavailable'}</p>
                    `;
                    break;
                case 'technical':
                    infoDiv.innerHTML = `
                        <div class="tech-image-details">
                            <span class="detail-name">variant:</span> <span class="detail-value">${index + 1}</span>
                            <span class="detail-name">style:</span> <span class="detail-value">${image.style || 'undefined'}</span>
                        </div>
                    `;
                    break;
                default:
                    infoDiv.innerHTML = `
                        <h4>Variant ${index + 1}</h4>
                        <p><i>Style: ${image.style || 'Default'}</i></p>
                    `;
            }
            
            imageCard.appendChild(infoDiv);
        } else {
            console.warn(`Image ${index} has no URL:`, image);
            const errorDiv = document.createElement('div');
            errorDiv.className = `image-error ${tone}-image-error`;
            errorDiv.textContent = 'Image URL not available';
            imageCard.appendChild(errorDiv);
        }
        
        // Add the card to the container
        imagesContainer.appendChild(imageCard);
    });
    
    // Add tone-specific prompt display
    if (imagePrompt && images[0] && images[0].prompt) {
        imagePrompt.className = `image-prompt ${tone}-image-prompt`;
        
        switch(tone) {
            case 'dramatic':
                imagePrompt.innerHTML = `<span class="prompt-label">Director's Notes:</span> "${images[0].prompt}"`;
                break;
            case 'poetic':
                imagePrompt.innerHTML = `<span class="prompt-label">Inspiration:</span> <em>${images[0].prompt}</em>`;
                break;
            case 'humorous':
                imagePrompt.innerHTML = `<span class="prompt-label">The Artist Was Told:</span> "${images[0].prompt}" 🎨`;
                break;
            case 'technical':
                imagePrompt.innerHTML = `<span class="prompt-label">// Generation parameters:</span><br>${images[0].prompt}`;
                break;
            case 'simple':
                imagePrompt.innerHTML = `<span class="prompt-label">Generated from:</span> ${images[0].prompt}`;
                break;
            default: // informative
                imagePrompt.innerHTML = `<span class="prompt-label">Prompt:</span> ${images[0].prompt}`;
        }
    } else if (imagePrompt) {
        // If prompt is missing, show a tone-specific message
        imagePrompt.className = `image-prompt ${tone}-image-prompt`;
        
        switch(tone) {
            case 'technical':
                imagePrompt.textContent = "// No generation parameters available";
                break;
            default:
                imagePrompt.textContent = "Image generation prompt not available";
        }
    }
}

/**
 * Display data sources information with tone-specific styling
 */
function displayDataSources(data) {
    if (!data) return;
    
    // Detect current tone from narrative container
    let tone = 'informative'; // Default tone
    const narrativeContainer = document.querySelector('.narrative-container');
    if (narrativeContainer) {
        // Extract tone from class name (e.g., tone-dramatic)
        const toneClass = Array.from(narrativeContainer.classList)
            .find(cls => cls.startsWith('tone-'));
        
        if (toneClass) {
            tone = toneClass.replace('tone-', '');
            console.log(`Applying ${tone} tone to data sources`);
        }
    }
    
    // Apply tone-specific class to data sources container
    const dataSourcesContainer = document.querySelector('.data-sources');
    if (dataSourcesContainer) {
        dataSourcesContainer.className = 'data-sources';
        dataSourcesContainer.classList.add(`${tone}-data-sources`);
    }
    
    // Wikipedia data
    const wikipediaDiv = document.getElementById('wikipedia-data');
    if (wikipediaDiv && data.wikipedia) {
        wikipediaDiv.className = `data-panel ${tone}-data-panel`;
        const title = document.createElement('h3');
        title.className = `${tone}-data-title`;
        
        switch(tone) {
            case 'dramatic':
                title.innerHTML = 'The Archive';
                break;
            case 'poetic':
                title.innerHTML = '✧ Knowledge Wellspring ✧';
                break;
            case 'humorous':
                title.innerHTML = 'The "Facts" 😉';
                break;
            case 'technical':
                title.innerHTML = '<span class="tech-symbol">&lt;</span>Wikipedia Data<span class="tech-symbol">&gt;</span>';
                break;
            case 'simple':
                title.innerHTML = 'Wikipedia';
                break;
            default: // informative
                title.innerHTML = 'Wikipedia Reference';
        }
        
        const content = document.createElement('div');
        content.className = `${tone}-data-content`;
        content.innerHTML = `
            <p>${data.wikipedia.summary}</p>
            ${data.wikipedia.url ? `<p class="${tone}-data-link"><a href="${data.wikipedia.url}" target="_blank">View on Wikipedia</a></p>` : ''}
        `;
        
        wikipediaDiv.innerHTML = '';
        wikipediaDiv.appendChild(title);
        wikipediaDiv.appendChild(content);
    }
    
    // News data
    const newsDiv = document.getElementById('news-data');
    if (newsDiv && data.news && data.news.length > 0) {
        newsDiv.className = `data-panel ${tone}-data-panel`;
        const title = document.createElement('h3');
        title.className = `${tone}-data-title`;
        
        switch(tone) {
            case 'dramatic':
                title.innerHTML = 'Recent Headlines';
                break;
            case 'poetic':
                title.innerHTML = '✧ Echoes of Now ✧';
                break;
            case 'humorous':
                title.innerHTML = 'Hot Off the Press! 🗞️';
                break;
            case 'technical':
                title.innerHTML = '<span class="tech-symbol">&lt;</span>News Data<span class="tech-symbol">&gt;</span>';
                break;
            case 'simple':
                title.innerHTML = 'News Articles';
                break;
            default: // informative
                title.innerHTML = 'Related News';
        }
        
        const content = document.createElement('div');
        content.className = `${tone}-data-content`;
        
        let newsHTML = '<ul class="${tone}-news-list">';
        data.news.forEach(article => {
            newsHTML += `
                <li class="${tone}-news-item">
                    <a href="${article.url}" target="_blank">${article.title}</a>
                    <small>${article.publisher || ''} ${article.published_at || ''}</small>
                </li>
            `;
        });
        newsHTML += '</ul>';
        
        content.innerHTML = newsHTML;
        
        newsDiv.innerHTML = '';
        newsDiv.appendChild(title);
        newsDiv.appendChild(content);
    } else if (newsDiv) {
        newsDiv.className = `data-panel ${tone}-data-panel`;
        const title = document.createElement('h3');
        title.className = `${tone}-data-title`;
        
        switch(tone) {
            case 'dramatic':
                title.innerHTML = 'Recent Headlines';
                break;
            case 'poetic':
                title.innerHTML = '✧ Echoes of Now ✧';
                break;
            case 'humorous':
                title.innerHTML = 'Hot Off the Press! 🗞️';
                break;
            case 'technical':
                title.innerHTML = '<span class="tech-symbol">&lt;</span>News Data<span class="tech-symbol">&gt;</span>';
                break;
            case 'simple':
                title.innerHTML = 'News Articles';
                break;
            default: // informative
                title.innerHTML = 'Related News';
        }
        
        const content = document.createElement('div');
        content.className = `${tone}-data-content`;
        
        switch(tone) {
            case 'dramatic':
                content.innerHTML = '<p>No recent headlines available for this topic.</p>';
                break;
            case 'poetic':
                content.innerHTML = '<p>The news pages remain silent on this subject.</p>';
                break;
            case 'humorous':
                content.innerHTML = '<p>Breaking news: No news! Reporters are still looking... 🕵️‍♀️</p>';
                break;
            case 'technical':
                content.innerHTML = '<p class="error-value">No news articles found in data source.</p>';
                break;
            default:
                content.innerHTML = '<p>No news articles found.</p>';
        }
        
        newsDiv.innerHTML = '';
        newsDiv.appendChild(title);
        newsDiv.appendChild(content);
    }
    
    // DBpedia data
    const dbpediaDiv = document.getElementById('dbpedia-data');
    if (dbpediaDiv && data.dbpedia) {
        dbpediaDiv.className = `data-panel ${tone}-data-panel`;
        const title = document.createElement('h3');
        title.className = `${tone}-data-title`;
        
        switch(tone) {
            case 'dramatic':
                title.innerHTML = 'Categories & Classifications';
                break;
            case 'poetic':
                title.innerHTML = '✧ Threads of Connection ✧';
                break;
            case 'humorous':
                title.innerHTML = 'Where It Fits In The Big Picture 🧩';
                break;
            case 'technical':
                title.innerHTML = '<span class="tech-symbol">&lt;</span>DBpedia Categories<span class="tech-symbol">&gt;</span>';
                break;
            case 'simple':
                title.innerHTML = 'Categories';
                break;
            default: // informative
                title.innerHTML = 'DBpedia Categories';
        }
        
        const content = document.createElement('div');
        content.className = `${tone}-data-content`;
        
        if (data.dbpedia.categories && data.dbpedia.categories.length > 0) {
            let categoriesHTML = `<ul class="${tone}-category-list">`;
            data.dbpedia.categories.forEach(category => {
                categoriesHTML += `<li class="${tone}-category-item">${category}</li>`;
            });
            categoriesHTML += '</ul>';
            content.innerHTML = categoriesHTML;
        } else {
            switch(tone) {
                case 'dramatic':
                    content.innerHTML = '<p>This subject defies conventional categorization.</p>';
                    break;
                case 'poetic':
                    content.innerHTML = '<p>Unbounded by categories, this subject exists beyond classification.</p>';
                    break;
                case 'humorous':
                    content.innerHTML = '<p>This topic is a rebel — it refuses to be put in a box! 📦</p>';
                    break;
                case 'technical':
                    content.innerHTML = '<p class="error-value">No category data found in knowledge graph.</p>';
                    break;
                default:
                    content.innerHTML = '<p>No categories found.</p>';
            }
        }
        
        dbpediaDiv.innerHTML = '';
        dbpediaDiv.appendChild(title);
        dbpediaDiv.appendChild(content);
    }
}

/**
 * Set up the conversation interface
 */
function setupConversation() {
    const chatInput = document.getElementById('chat-input');
    const chatSubmit = document.getElementById('chat-submit');
    const chatHistory = document.getElementById('chat-history');
    
    if (!chatInput || !chatSubmit || !chatHistory) {
        console.warn("Conversation elements not found");
        return;
    }
    
    // Store conversation context and history
    const conversationContext = {
        topic: "",
        tone: "informative",
        history: []
    };
    
    // Handle Enter key in textarea
    chatInput.addEventListener('keydown', function(e) {
        // Check if Enter was pressed without Shift key
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatSubmit.click();
        }
    });
    
    // Handle message submission
    chatSubmit.addEventListener('click', async function() {
        const message = chatInput.value.trim();
        
        // Don't send empty messages
        if (!message) {
            return;
        }
        
        // Disable input while processing
        chatInput.disabled = true;
        chatSubmit.disabled = true;
        
        try {
            // Display user message
            addUserMessage(message);
            
            // Clear input
            chatInput.value = '';
            
            // Show typing indicator
            const typingIndicator = addTypingIndicator();
            
            // Ensure we have a topic
            if (!conversationContext.topic) {
                const topicHeading = document.getElementById('topic-heading');
                if (topicHeading) {
                    conversationContext.topic = topicHeading.textContent;
                }
                
                // Update conversation topic display
                const conversationTopic = document.getElementById('conversation-topic');
                if (conversationTopic) {
                    conversationTopic.textContent = conversationContext.topic;
                }
            }
            
            // Determine current tone
            const narrativeContainer = document.querySelector('.narrative-container');
            if (narrativeContainer) {
                // Extract tone from class name (e.g., tone-dramatic)
                const toneClass = Array.from(narrativeContainer.classList)
                    .find(cls => cls.startsWith('tone-'));
                
                if (toneClass) {
                    conversationContext.tone = toneClass.replace('tone-', '');
                }
            }
            
            // Add user message to history
            conversationContext.history.push({
                role: 'user',
                content: message
            });
            
            // Get current temperature value if advanced options are visible
            let temperature = 0.7; // Default
            const advancedOptions = document.getElementById('advanced-options');
            const temperatureInput = document.getElementById('temperature');
            
            if (advancedOptions && !advancedOptions.classList.contains('hidden') && temperatureInput) {
                temperature = parseFloat(temperatureInput.value) || 0.7;
            }
            
            // Send to API
            const response = await fetch('/api/conversation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    topic: conversationContext.topic,
                    question: message,
                    conversation_history: conversationContext.history,
                    tone: conversationContext.tone,
                    temperature: temperature
                })
            });
            
            // Remove typing indicator
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            // Process response
            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to get response');
            }
            
            // Display AI message
            addAIMessage(data.response, data.references);
            
            // Add to conversation history
            conversationContext.history.push({
                role: 'ai',
                content: data.response
            });
            
        } catch (error) {
            console.error('Conversation error:', error);
            
            // Display error message
            addSystemMessage(`Sorry, I couldn't process your message: ${error.message}`);
            
        } finally {
            // Re-enable input
            chatInput.disabled = false;
            chatSubmit.disabled = false;
            chatInput.focus();
        }
    });
    
    // Helper to add a user message to the chat
    function addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message user-message';
        
        const messagePara = document.createElement('p');
        messagePara.textContent = text;
        messageDiv.appendChild(messagePara);
        
        chatHistory.appendChild(messageDiv);
        
        // Scroll to bottom
        chatHistory.scrollTop = chatHistory.scrollHeight;
        
        return messageDiv;
    }
    
    // Helper to add an AI message to the chat
    function addAIMessage(text, references = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message ai-message';
        
        // Safely create HTML content
        const responseContent = document.createElement('p');
        
        // Process the response text for any markdown-like formatting
        let formattedText = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
        
        responseContent.innerHTML = formattedText;
        messageDiv.appendChild(responseContent);
        
        // Add references if any
        if (references && references.length > 0) {
            const referencesDiv = document.createElement('div');
            referencesDiv.className = 'reference';
            
            const referencesContent = document.createElement('p');
            referencesContent.innerHTML = references.map(ref => {
                // Try to detect URLs and make them links
                const urlMatch = ref.match(/(https?:\/\/[^\s]+)/g);
                if (urlMatch) {
                    return ref.replace(urlMatch[0], `<a href="${urlMatch[0]}" target="_blank">${urlMatch[0]}</a>`);
                }
                return ref;
            }).join('<br>');
            
            referencesDiv.appendChild(referencesContent);
            messageDiv.appendChild(referencesDiv);
        }
        
        chatHistory.appendChild(messageDiv);
        
        // Scroll to bottom
        chatHistory.scrollTop = chatHistory.scrollHeight;
        
        return messageDiv;
    }
    
    // Helper to add a system message
    function addSystemMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'system-message';
        
        const messagePara = document.createElement('p');
        messagePara.textContent = text;
        messageDiv.appendChild(messagePara);
        
        chatHistory.appendChild(messageDiv);
        
        // Scroll to bottom
        chatHistory.scrollTop = chatHistory.scrollHeight;
        
        return messageDiv;
    }
    
    // Helper to add typing indicator
    function addTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        
        // Add the dots
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            indicator.appendChild(dot);
        }
        
        chatHistory.appendChild(indicator);
        
        // Scroll to bottom
        chatHistory.scrollTop = chatHistory.scrollHeight;
        
        return indicator;
    }
} 

/**
 * Setup enhanced dynamic form elements
 */
function setupDynamicFormElements() {
    // Animated form field focus effects
    const formInputs = document.querySelectorAll('input[type="text"], input[type="number"], select, textarea');
    
    formInputs.forEach(input => {
        // Create a ripple effect container for each input
        const rippleContainer = document.createElement('div');
        rippleContainer.className = 'input-focus-ripple';
        input.parentNode.appendChild(rippleContainer);
        
        // Add focus animations
        input.addEventListener('focus', function() {
            this.parentNode.classList.add('input-focused');
            
            // Create ripple effect
            rippleContainer.innerHTML = '';
            const ripple = document.createElement('span');
            rippleContainer.appendChild(ripple);
            ripple.addEventListener('animationend', () => {
                ripple.remove();
            });
        });
        
        // Remove focus animations
        input.addEventListener('blur', function() {
            this.parentNode.classList.remove('input-focused');
        });
        
        // Add active class if input has value
        if (input.value) {
            input.parentNode.classList.add('input-has-value');
        }
        
        input.addEventListener('input', function() {
            if (this.value) {
                this.parentNode.classList.add('input-has-value');
            } else {
                this.parentNode.classList.remove('input-has-value');
            }
        });
    });
    
    // Enhanced range inputs
    const rangeInputs = document.querySelectorAll('input[type="range"]');
    
    rangeInputs.forEach(range => {
        function updateRangeValue() {
            const value = range.value;
            const min = range.min || 0;
            const max = range.max || 100;
            const percentage = ((value - min) / (max - min)) * 100;
            
            // Update the background gradient
            range.style.background = `linear-gradient(to right, var(--color-purple) 0%, var(--color-purple) ${percentage}%, rgba(50, 50, 70, 0.5) ${percentage}%, rgba(50, 50, 70, 0.5) 100%)`;
            
            // Add animation to the value display
            const valueDisplay = range.parentNode.querySelector('[id$="-value"]');
            if (valueDisplay) {
                valueDisplay.textContent = value;
                valueDisplay.classList.add('changing');
                setTimeout(() => {
                    valueDisplay.classList.remove('changing');
                }, 300);
            }
        }
        
        // Initialize range visuals
        updateRangeValue();
        
        // Update on input change
        range.addEventListener('input', updateRangeValue);
    });
    
    // Tone selector visual enhancement
    const toneSelector = document.getElementById('tone');
    if (toneSelector) {
        toneSelector.addEventListener('change', function() {
            // Add a visual effect indicating the tone change
            const selectedTone = this.value;
            const toneEffect = document.createElement('div');
            toneEffect.className = `tone-transition-effect tone-${selectedTone}`;
            document.body.appendChild(toneEffect);
            
            setTimeout(() => {
                toneEffect.classList.add('active');
            }, 10);
            
            setTimeout(() => {
                toneEffect.classList.remove('active');
                setTimeout(() => toneEffect.remove(), 500);
            }, 1000);
        });
    }
    
    // Fix advanced options toggle
    const advancedBtn = document.getElementById('advanced-btn');
    const advancedOptions = document.getElementById('advanced-options');
    
    if (advancedBtn && advancedOptions) {
        // Ensure proper initialization of text
        if (advancedOptions.classList.contains('hidden')) {
            advancedBtn.querySelector('.btn-text').textContent = 'Advanced Options';
        } else {
            advancedBtn.querySelector('.btn-text').textContent = 'Hide Advanced Options';
        }
        
        advancedBtn.addEventListener('click', function() {
            // Toggle visibility with proper class toggling
            advancedOptions.classList.toggle('hidden');
            
            // Update button text based on the current state
            const btnText = advancedOptions.classList.contains('hidden')
                ? 'Advanced Options'
                : 'Hide Advanced Options';
            
            this.querySelector('.btn-text').textContent = btnText;
            
            // Smooth scroll to advanced options when shown
            if (!advancedOptions.classList.contains('hidden')) {
                setTimeout(() => {
                    advancedOptions.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }, 400);
                
                // Trigger a focus state on the first input for better UX
                const firstInput = advancedOptions.querySelector('input, select');
                if (firstInput) {
                    setTimeout(() => {
                        firstInput.focus();
                    }, 500);
                }
            }
        });
    }
    
    // Improve topic input user experience
    const topicInput = document.getElementById('topic');
    if (topicInput) {
        // Ensure form recognizes prefilled values
        if (topicInput.value) {
            topicInput.parentNode.classList.add('input-has-value');
        }
        
        // Auto focus on page load
        setTimeout(() => {
            topicInput.focus();
        }, 500);
        
        // Add suggestions as you type
        topicInput.addEventListener('input', function() {
            // Check for existing suggestion container
            let suggestionContainer = document.querySelector('.topic-suggestions');
            
            // Create if it doesn't exist
            if (!suggestionContainer && this.value.length >= 2) {
                suggestionContainer = document.createElement('div');
                suggestionContainer.className = 'topic-suggestions';
                this.parentNode.appendChild(suggestionContainer);
                
                // Position it properly below the input
                const inputRect = this.getBoundingClientRect();
                suggestionContainer.style.width = inputRect.width + 'px';
                suggestionContainer.style.top = (this.offsetHeight + 5) + 'px';
            }
            
            // Clear if input is too short
            if (this.value.length < 2 && suggestionContainer) {
                suggestionContainer.remove();
                return;
            }
            
            // Generate suggestions based on input
            if (suggestionContainer && this.value.length >= 2) {
                // Sample suggestions - in a real app, these would come from an API
                const suggestions = [
                    'Quantum Physics',
                    'Artificial Intelligence',
                    'French Revolution',
                    'Climate Change',
                    'Space Exploration',
                    'Blockchain Technology',
                    'Renaissance Art',
                    'Marine Biology',
                    'Ancient Egypt'
                ];
                
                // Filter suggestions based on input
                const filtered = suggestions.filter(s => 
                    s.toLowerCase().includes(this.value.toLowerCase())
                ).slice(0, 3); // Limit to 3 suggestions
                
                if (filtered.length > 0) {
                    suggestionContainer.innerHTML = '';
                    filtered.forEach(suggestion => {
                        const item = document.createElement('div');
                        item.className = 'suggestion-item';
                        item.textContent = suggestion;
                        
                        // Apply the suggestion when clicked
                        item.addEventListener('click', () => {
                            topicInput.value = suggestion;
                            topicInput.parentNode.classList.add('input-has-value');
                            suggestionContainer.remove();
                            
                            // Trigger a focus event on a different field
                            const toneSelect = document.getElementById('tone');
                            if (toneSelect) {
                                setTimeout(() => {
                                    toneSelect.focus();
                                }, 100);
                            }
                        });
                        
                        suggestionContainer.appendChild(item);
                    });
                } else {
                    suggestionContainer.remove();
                }
            }
        });
        
        // Remove suggestions when clicking elsewhere
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.floating-label')) {
                const suggestions = document.querySelector('.topic-suggestions');
                if (suggestions) {
                    suggestions.remove();
                }
            }
        });
    }
    
    // Add CSS for topic suggestions
    const style = document.createElement('style');
    style.textContent = `
        .topic-suggestions {
            position: absolute;
            z-index: 100;
            background: rgba(20, 20, 30, 0.95);
            border-radius: 8px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(139, 92, 246, 0.3);
            overflow: hidden;
            max-height: 0;
            transition: max-height 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            animation: dropDown 0.3s forwards;
        }
        
        @keyframes dropDown {
            from { max-height: 0; opacity: 0; }
            to { max-height: 150px; opacity: 1; }
        }
        
        .suggestion-item {
            padding: 10px 15px;
            cursor: pointer;
            transition: background 0.2s ease;
            font-size: 14px;
        }
        
        .suggestion-item:hover {
            background: rgba(139, 92, 246, 0.2);
        }
    `;
    document.head.appendChild(style);
}

// Initialize form validation
function setupFormValidation() {
    const generateForm = document.getElementById('generate-form');
    
    if (generateForm) {
        // Prevent form submission if topic is empty
        generateForm.addEventListener('submit', function(e) {
            const topicInput = document.getElementById('topic');
            
            if (!topicInput || !topicInput.value.trim()) {
                e.preventDefault();
                
                // Add shake animation to input
                topicInput.classList.add('shake-error');
                setTimeout(() => {
                    topicInput.classList.remove('shake-error');
                }, 500);
                
                // Focus the input
                topicInput.focus();
                
                // Show error message
                const errorMsg = document.createElement('div');
                errorMsg.className = 'input-error';
                errorMsg.textContent = 'Please enter a topic';
                
                // Remove any existing error message
                const existingError = topicInput.parentNode.querySelector('.input-error');
                if (existingError) {
                    existingError.remove();
                }
                
                topicInput.parentNode.appendChild(errorMsg);
                
                // Remove error after 3 seconds
                setTimeout(() => {
                    if (errorMsg.parentNode) {
                        errorMsg.remove();
                    }
                }, 3000);
                
                return false;
            }
            
            return true;
        });
    }
}

// Add styling for validation
const validationStyle = document.createElement('style');
validationStyle.textContent = `
    .shake-error {
        animation: shakeInput 0.5s cubic-bezier(.36,.07,.19,.97) both;
        transform: translate3d(0, 0, 0);
        border-color: #f44336 !important;
        box-shadow: 0 0 0 2px rgba(244, 67, 54, 0.2) !important;
    }
    
    @keyframes shakeInput {
        10%, 90% { transform: translate3d(-1px, 0, 0); }
        20%, 80% { transform: translate3d(2px, 0, 0); }
        30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
        40%, 60% { transform: translate3d(4px, 0, 0); }
    }
    
    .input-error {
        color: #f44336;
        font-size: 0.875rem;
        margin-top: 0.5rem;
        animation: fadeIn 0.3s ease;
        position: absolute;
        bottom: -20px;
        left: 0;
    }
`;
document.head.appendChild(validationStyle);

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Restore theme from localStorage if it exists
    const savedTone = localStorage.getItem('selectedTone');
    if (savedTone) {
        document.body.classList.add(`tone-${savedTone}`);
        
        // Also update the tone selector
        const toneSelector = document.getElementById('tone');
        if (toneSelector) {
            toneSelector.value = savedTone;
        }
    } else {
        // Default tone
        document.body.classList.add('tone-informative');
    }
    
    // Set up application components - conditionally call functions based on element presence
    if (document.querySelectorAll('.tab-link').length > 0) {
        setupTabs();
    }
    
    // Only call setupRangeInputs if at least one range input exists
    if (document.getElementById('variants') || document.getElementById('temperature')) {
        setupRangeInputs();
    }
    
    // setupAdvancedOptions already has internal checks for element existence
    if (document.getElementById('advanced-btn')) {
        setupAdvancedOptions();
    }
    
    if (document.getElementById('generate-form')) {
        setupGenerateForm();
    }
    
    if (document.getElementById('expertise_level')) {
        setupExpertiseLevel();
    }
    
    setupUIEnhancements();
    
    // Check API status
    checkApiStatus();
    
    console.log("CONTRA application initialized");
    
    setupDynamicFormElements();
    setupFormValidation();
    
    // Always show visualization tab regardless of data availability
    showVisualizationTab();
    
    // DON'T initialize visualizations on page load
    // This will be done when the user clicks on the visualization tab
});

/**
 * Check the status of API integrations and show warnings if needed
 */
async function checkApiStatus() {
    try {
        const response = await fetch('/api/status');
        if (!response.ok) {
            console.warn("Failed to check API status:", response.status);
            return;
        }
        
        const data = await response.json();
        if (!data.success) {
            console.warn("API status check returned error:", data.error);
            return;
        }
        
        const status = data.status;
        let warnings = [];
        let missingApis = [];
        
        // Check stability API status
        if (status.stability_ai && !status.stability_ai.available) {
            warnings.push({
                service: "Stability AI",
                message: "Image generation is unavailable due to missing or invalid API key.",
                details: "Some features requiring image generation may not work properly."
            });
            missingApis.push("Stability AI (images)");
        }
        
        // Check other APIs as needed
        if (status.groq && !status.groq.available) {
            warnings.push({
                service: "Groq",
                message: "Groq LLM service is unavailable due to missing or invalid API key.",
                details: "Narrative generation may be limited or unavailable."
            });
            missingApis.push("Groq (narrative)");
        }
        
        if (status.news_api && !status.news_api.available) {
            warnings.push({
                service: "News API",
                message: "News API service is unavailable due to missing or invalid API key.",
                details: "News data will not be available for topics."
            });
            missingApis.push("News API (data sources)");
        }
        
        // Display warnings if any
        if (warnings.length > 0) {
            // Show notification popups
            displayApiWarnings(warnings);
            
            // If multiple APIs are missing, display a banner at the top of the page
            if (missingApis.length > 1) {
                displayApiStatusBanner(missingApis, data.overall);
            }
        }
    } catch (error) {
        console.error("Error checking API status:", error);
    }
}

/**
 * Display a banner at the top of the page for missing API keys
 */
function displayApiStatusBanner(missingApis, overallStatus) {
    // Create banner element
    const banner = document.createElement('div');
    banner.className = 'api-status-banner';
    
    // Create content based on missing APIs
    const apiList = missingApis.join(', ');
    banner.innerHTML = `
        <div class="api-banner-content">
            <h4>⚠️ API Configuration Required</h4>
            <p>Missing API keys: ${apiList}</p>
            <p class="banner-details">Some features may be limited or unavailable. Please configure your API keys to enable full functionality.</p>
        </div>
        <button class="dismiss-banner">✕</button>
    `;
    
    // Add styles for the banner
    const style = document.createElement('style');
    style.textContent = `
        .api-status-banner {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(10px);
            color: #e5e7eb;
            padding: 0.75rem 1.5rem;
            z-index: 2000;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            transform: translateY(-100%);
            animation: slideDown 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        
        .api-banner-content {
            flex: 1;
        }
        
        .api-status-banner h4 {
            margin: 0 0 0.25rem;
            color: #f59e0b;
            font-size: 1rem;
        }
        
        .api-status-banner p {
            margin: 0;
            font-size: 0.875rem;
        }
        
        .banner-details {
            font-size: 0.8rem;
            color: #9ca3af;
            margin-top: 0.25rem !important;
        }
        
        .dismiss-banner {
            background: transparent;
            border: none;
            color: #9ca3af;
            font-size: 1.25rem;
            cursor: pointer;
            margin-left: 1rem;
            padding: 0.25rem;
            line-height: 1;
        }
        
        .dismiss-banner:hover {
            color: #e5e7eb;
        }
        
        @keyframes slideDown {
            from {
                transform: translateY(-100%);
            }
            to {
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
    
    // Add to body
    document.body.prepend(banner);
    
    // Add dismiss functionality
    const dismissButton = banner.querySelector('.dismiss-banner');
    if (dismissButton) {
        dismissButton.addEventListener('click', function() {
            banner.style.animation = 'slideUp 0.3s cubic-bezier(0.22, 1, 0.36, 1) forwards';
            
            // Add animation for slide up
            const slideUpStyle = document.createElement('style');
            slideUpStyle.textContent = `
                @keyframes slideUp {
                    from {
                        transform: translateY(0);
                    }
                    to {
                        transform: translateY(-100%);
                    }
                }
            `;
            document.head.appendChild(slideUpStyle);
            
            // Remove after animation
            setTimeout(() => {
                if (banner.parentNode) {
                    banner.parentNode.removeChild(banner);
                }
            }, 300);
        });
    }
    
    // Adjust page padding to account for banner
    setTimeout(() => {
        const bannerHeight = banner.offsetHeight;
        document.body.style.paddingTop = `${bannerHeight}px`;
    }, 500);
}

/**
 * Display warnings about API status issues
 */
function displayApiWarnings(warnings) {
    // Create container for warnings if it doesn't exist
    let warningsContainer = document.getElementById('api-warnings');
    if (!warningsContainer) {
        warningsContainer = document.createElement('div');
        warningsContainer.id = 'api-warnings';
        warningsContainer.className = 'api-warnings-container';
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .api-warnings-container {
                position: fixed;
                top: 80px;
                right: 20px;
                z-index: 1000;
                max-width: 350px;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            
            .api-warning {
                background: rgba(15, 23, 42, 0.8);
                backdrop-filter: blur(10px);
                border-radius: 8px;
                padding: 1rem;
                border-left: 4px solid #f59e0b;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                font-size: 0.875rem;
                animation: slideIn 0.3s ease;
                color: #e5e7eb;
            }
            
            .api-warning h4 {
                margin-top: 0;
                margin-bottom: 0.5rem;
                color: #f59e0b;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .api-warning h4::before {
                content: '⚠️';
            }
            
            .api-warning p {
                margin: 0 0 0.5rem;
            }
            
            .api-warning .details {
                font-size: 0.8rem;
                color: #9ca3af;
                margin: 0;
            }
            
            .dismiss-warning {
                position: absolute;
                top: 8px;
                right: 8px;
                background: transparent;
                border: none;
                color: #9ca3af;
                font-size: 16px;
                cursor: pointer;
                padding: 2px;
                line-height: 1;
            }
            
            .dismiss-warning:hover {
                color: #e5e7eb;
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(50px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes fadeOut {
                from {
                    opacity: 1;
                    transform: translateX(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(50px);
                }
            }
        `;
        document.head.appendChild(style);
        
        // Add container to body
        document.body.appendChild(warningsContainer);
    }
    
    // Add each warning
    warnings.forEach((warning, index) => {
        const warningElement = document.createElement('div');
        warningElement.className = 'api-warning';
        warningElement.style.animationDelay = `${index * 0.1}s`;
        
        warningElement.innerHTML = `
            <h4>${warning.service} Warning</h4>
            <p>${warning.message}</p>
            <p class="details">${warning.details}</p>
            <button class="dismiss-warning" aria-label="Dismiss warning">×</button>
        `;
        
        // Add dismiss button functionality
        const dismissButton = warningElement.querySelector('.dismiss-warning');
        dismissButton.addEventListener('click', function() {
            warningElement.style.animation = 'fadeOut 0.3s ease forwards';
            setTimeout(() => {
                if (warningElement.parentNode) {
                    warningElement.parentNode.removeChild(warningElement);
                }
                
                // If no more warnings, remove the container
                if (warningsContainer.children.length === 0) {
                    warningsContainer.parentNode.removeChild(warningsContainer);
                }
            }, 300);
        });
        
        warningsContainer.appendChild(warningElement);
        
        // Auto dismiss after 10 seconds
        setTimeout(() => {
            if (warningElement.parentNode) {
                warningElement.style.animation = 'fadeOut 0.3s ease forwards';
                setTimeout(() => {
                    if (warningElement.parentNode) {
                        warningElement.parentNode.removeChild(warningElement);
                    }
                    
                    // If no more warnings, remove the container
                    if (warningsContainer.children.length === 0 && warningsContainer.parentNode) {
                        warningsContainer.parentNode.removeChild(warningsContainer);
                    }
                }, 300);
            }
        }, 10000 + (index * 1000));
    });
}

/**
 * Set up additional UI enhancements
 */
function setupUIEnhancements() {
    // Add active state to navbar links based on current page
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Add parallax effect to hero section
    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', function() {
            const scrollPosition = window.scrollY;
            if (scrollPosition < 600) {
                const translateY = scrollPosition * 0.3;
                hero.style.backgroundPosition = `center ${translateY}px`;
            }
        });
    }
    
    // Add intersection observer for scroll animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    // Observe elements that should animate on scroll
    document.querySelectorAll('.narrative-container, .image-card, .viz-panel, .data-panel').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Set up tab switching functionality
 */
function setupTabs() {
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');
    
    if (!tabLinks.length) {
        console.warn("No tab links found");
        return;
    }
    
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Skip if tab is hidden (display: none)
            if (this.parentElement.style.display === 'none') {
                console.log("Attempted to click hidden tab, ignoring");
                return;
            }
            
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all tabs and contents
            tabLinks.forEach(tab => tab.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab and content
            this.classList.add('active');
            document.getElementById(`${targetTab}-tab`).classList.add('active');
            
            // Initialize visualizations when the visualization tab is clicked
            if (targetTab === 'visualizations') {
                // Check if visualizations have been initialized
                const vizInitialized = document.querySelector('.viz-panel').getAttribute('data-initialized');
                if (vizInitialized !== 'true') {
                    console.log('Initializing visualizations on tab click');
                    initVisualizations();
                    // Mark the visualization panel as initialized
                    document.querySelectorAll('.viz-panel').forEach(panel => {
                        panel.setAttribute('data-initialized', 'true');
                    });
                }
            }
            
            // Scroll to top of tab content smoothly
            const tabContent = document.getElementById(`${targetTab}-tab`);
            if (tabContent) {
                const topOffset = tabContent.offsetTop - 100; // Adjust for fixed header
                window.scrollTo({
                    top: topOffset,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Function to find first visible tab
    const getFirstVisibleTab = () => {
        for (const link of tabLinks) {
            if (link.parentElement.style.display !== 'none') {
                return link;
            }
        }
        return tabLinks[0]; // Default to first tab if none are visible
    };
    
    // Public method to activate a specific tab by name
    window.activateTab = (tabName) => {
        const tabLink = document.querySelector(`.tab-link[data-tab="${tabName}"]`);
        if (tabLink && tabLink.parentElement.style.display !== 'none') {
            tabLink.click();
            return true;
        }
        // If tab not found or hidden, activate first visible tab
        const firstVisibleTab = getFirstVisibleTab();
        if (firstVisibleTab) {
            firstVisibleTab.click();
        }
        return false;
    };
}

/**
 * Set up range input displays
 */
function setupRangeInputs() {
    const setupRange = (inputId, valueId) => {
        const input = document.getElementById(inputId);
        const value = document.getElementById(valueId);
        
        if (input && value) {
            // Set initial value
            value.textContent = input.value;
            
            // Update value on input
            input.addEventListener('input', function() {
                value.textContent = this.value;
                // Add a subtle animation effect
                value.style.transform = 'scale(1.2)';
                setTimeout(() => {
                    value.style.transform = 'scale(1)';
                }, 200);
            });
        }
    };
    
    // Only setup range inputs if they exist on the page
    if (document.getElementById('variants')) {
        setupRange('variants', 'variants-value');
    }
    
    if (document.getElementById('temperature')) {
        setupRange('temperature', 'temperature-value');
    }
}

/**
 * Set up advanced options toggle
 */
function setupAdvancedOptions() {
    const advancedBtn = document.getElementById('advanced-btn');
    const advancedOptions = document.getElementById('advanced-options');
    
    if (advancedBtn && advancedOptions) {
        // Initialize button text
        advancedBtn.textContent = advancedOptions.classList.contains('hidden') 
            ? 'Advanced Options' 
            : 'Hide Advanced Options';
        
        advancedBtn.addEventListener('click', function() {
            advancedOptions.classList.toggle('hidden');
            
            // Update button text based on the current state
            this.textContent = advancedOptions.classList.contains('hidden')
                ? 'Advanced Options'
                : 'Hide Advanced Options';
            
            // Smooth scroll to advanced options when shown
            if (!advancedOptions.classList.contains('hidden')) {
                setTimeout(() => {
                    advancedOptions.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }, 100);
            }
        });
    }
}

/**
 * Initialize visualizations for the data
 */
function initVisualizations() {
    console.log('Initializing visualizations');
    
    // Check if we have stored visualization data
    const vizDataInput = document.getElementById('visualization-data');
    let storedVizData = null;
    
    if (vizDataInput && vizDataInput.value) {
        try {
            storedVizData = JSON.parse(vizDataInput.value);
            console.log('Found stored visualization data', storedVizData);
        } catch (e) {
            console.error('Error parsing stored visualization data', e);
        }
    }
    
    // If we have stored data, use it
    if (storedVizData) {
        displayVisualizations(storedVizData);
        return;
    }
    
    // Otherwise, create default visualizations
    console.log('Using default visualizations');
    
    // Timeline visualization
    const timelineData = {
        x: [1576],
        y: [1],
        mode: 'markers+lines',
        type: 'scatter',
        marker: {
            size: 15,
            color: 'rgb(139, 92, 246)',
            line: {
                color: 'white',
                width: 2
            }
        },
        line: {
            color: 'rgba(139, 92, 246, 0.5)',
            width: 2,
            dash: 'dash'
        },
        name: 'Battle of Haldighati',
        hoverinfo: 'text',
        hoverlabel: {
            bgcolor: 'rgba(0, 0, 0, 0.8)',
            bordercolor: 'rgb(139, 92, 246)',
            font: { color: 'white' }
        },
        text: ['Battle of Haldighati (1576): Maharana Pratap vs Mughal Empire'],
        hovertext: [
            ['Emperor Akbar of Mughal Empire', 'Conflict between Akbar and Pratap', 'Akbar\'s forces against Rajputs'],
            ['Mughal defeat of Mewar forces', 'Maharana Pratap ruled Mewar', 'Mewar Rajputs fought bravely'],
            ['Battle between empires', 'Battle led by Pratap', 'Rajput warriors in battle']
        ]
    };
    
    const timelineLayout = {
        title: 'Timeline of Key Events',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {
            color: 'white'
        },
        xaxis: {
            title: 'Year',
            showgrid: true,
            gridcolor: 'rgba(255,255,255,0.1)',
            tickcolor: 'white'
        },
        yaxis: {
            title: 'Significance',
            showgrid: true,
            gridcolor: 'rgba(255,255,255,0.1)',
            tickcolor: 'white'
        },
        hovermode: 'closest',
        margin: {
            l: 60,
            r: 30,
            b: 60,
            t: 80,
            pad: 10
        }
    };
    
    const timelineConfig = {
        responsive: true,
        displayModeBar: false
    };
    
    const timelineElement = document.getElementById('timeline-viz');
    if (timelineElement) {
        Plotly.newPlot('timeline-viz', [timelineData], timelineLayout, timelineConfig);
    }
    
    // Categories visualization
    const categoriesData = [{
        type: 'sunburst',
        labels: ['Battle of Haldighati', 'Participants', 'Locations', 'Outcomes', 'Mughal Empire', 'Mewar Kingdom', 'Haldighati', 'Rajasthan', 'Tactical Retreat', 'Cultural Legacy'],
        parents: ['', 'Battle of Haldighati', 'Battle of Haldighati', 'Battle of Haldighati', 'Participants', 'Participants', 'Locations', 'Locations', 'Outcomes', 'Outcomes'],
        values: [10, 5, 4, 5, 3, 3, 2, 2, 2, 3],
        outsidetextfont: {size: 20, color: "#377eb8"},
        marker: {
            line: {width: 2, color: 'rgba(0,0,0,0.2)'}
        },
        insidetextfont: {
            color: 'white'
        }
    }];
    
    const categoriesLayout = {
        title: 'Categories & Entities',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {
            color: 'white'
        },
        margin: {
            l: 20,
            r: 20,
            b: 20,
            t: 80,
        }
    };
    
    const categoriesConfig = {
        responsive: true,
        displayModeBar: false
    };
    
    const categoriesElement = document.getElementById('categories-viz');
    if (categoriesElement) {
        Plotly.newPlot('categories-viz', categoriesData, categoriesLayout, categoriesConfig);
    }
    
    // Relationships visualization
    const relationshipsData = [{
        type: 'sankey',
        orientation: 'h',
        node: {
            pad: 15,
            thickness: 20,
            line: {
                color: 'rgba(0,0,0,0.2)',
                width: 0.5
            },
            label: ['Akbar', 'Maharana Pratap', 'Man Singh', 'Jhala', 'Battle of Haldighati', 'Mewar Kingdom', 'Mughal Empire', 'Rajput Clans', 'Chetak'],
            color: ['rgba(139, 92, 246, 0.8)', 'rgba(139, 92, 246, 0.8)', 'rgba(139, 92, 246, 0.8)', 
                    'rgba(139, 92, 246, 0.8)', 'rgba(239, 68, 68, 0.8)', 'rgba(6, 182, 212, 0.8)', 
                    'rgba(6, 182, 212, 0.8)', 'rgba(6, 182, 212, 0.8)', 'rgba(139, 92, 246, 0.8)']
        },
        link: {
            source: [0, 0, 1, 1, 2, 3, 4, 5, 6, 7, 1],
            target: [4, 6, 4, 5, 4, 1, 5, 7, 0, 1, 8],
            value: [5, 8, 5, 10, 3, 4, 6, 5, 8, 5, 3],
            color: ['rgba(139, 92, 246, 0.3)', 'rgba(6, 182, 212, 0.3)', 'rgba(139, 92, 246, 0.3)', 
                    'rgba(6, 182, 212, 0.3)', 'rgba(139, 92, 246, 0.3)', 'rgba(6, 182, 212, 0.3)', 
                    'rgba(239, 68, 68, 0.3)', 'rgba(6, 182, 212, 0.3)', 'rgba(6, 182, 212, 0.3)', 
                    'rgba(6, 182, 212, 0.3)', 'rgba(139, 92, 246, 0.3)']
        }
    }];
    
    const relationshipsLayout = {
        title: 'Key Relationships & Influence',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {
            color: 'white'
        },
        margin: {
            l: 20,
            r: 20,
            b: 20,
            t: 80,
        }
    };
    
    const relationshipsConfig = {
        responsive: true,
        displayModeBar: false
    };
    
    const relationshipsElement = document.getElementById('relationships-viz');
    if (relationshipsElement) {
        Plotly.newPlot('relationships-viz', relationshipsData, relationshipsLayout, relationshipsConfig);
    }
    
    // Setup fullscreen functionality for visualizations
    setupFullscreenViz();
    
    console.log('Visualizations initialized successfully');
}

/**
 * Setup fullscreen buttons for visualizations
 */
function setupFullscreenButtons() {
    const fullscreenButtons = document.querySelectorAll('.viz-fullscreen-btn');
    
    fullscreenButtons.forEach(button => {
        button.addEventListener('click', function() {
            const vizPanel = this.closest('.viz-panel');
            const vizContainer = vizPanel.querySelector('.viz-timeline, .viz-categories, .viz-concept-map');
            
            if (!document.fullscreenElement) {
                if (vizPanel.requestFullscreen) {
                    vizPanel.requestFullscreen();
                } else if (vizPanel.webkitRequestFullscreen) {
                    vizPanel.webkitRequestFullscreen();
                } else if (vizPanel.msRequestFullscreen) {
                    vizPanel.msRequestFullscreen();
                }
                
                this.innerHTML = '<i class="fas fa-compress"></i>';
                
                // Resize plot when entering fullscreen
                setTimeout(() => {
                    if (vizContainer.id === 'timeline-viz') {
                        Plotly.relayout('timeline-viz', {
                            'xaxis.titlefont.size': 16,
                            'xaxis.tickfont.size': 14,
                            'margin': { t: 50, b: 80, l: 50, r: 50 }
                        });
                    } else if (vizContainer.id === 'categories-viz') {
                        Plotly.relayout('categories-viz', {
                            'xaxis.titlefont.size': 16,
                            'yaxis.titlefont.size': 16,
                            'xaxis.tickfont.size': 14,
                            'yaxis.tickfont.size': 14,
                            'margin': { t: 50, b: 80, l: 250, r: 50 }
                        });
                    } else if (vizContainer.id === 'concept-map-viz') {
                        Plotly.relayout('concept-map-viz', {
                            'xaxis.tickfont.size': 14,
                            'yaxis.tickfont.size': 14,
                            'margin': { t: 50, b: 120, l: 150, r: 50 }
                        });
                    }
                }, 500);
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                } else if (document.msExitFullscreen) {
                    document.msExitFullscreen();
                }
                
                this.innerHTML = '<i class="fas fa-expand"></i>';
            }
        });
    });
    
    // Handle fullscreen change
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('MSFullscreenChange', handleFullscreenChange);
}

/**
 * Handle fullscreen change event
 */
function handleFullscreenChange() {
    if (!document.fullscreenElement && 
        !document.webkitFullscreenElement && 
        !document.mozFullscreenElement && 
        !document.msFullscreenElement) {
        
        // Reset all fullscreen buttons
        document.querySelectorAll('.viz-fullscreen-btn').forEach(btn => {
            btn.innerHTML = '<i class="fas fa-expand"></i>';
        });
        
        // Resize plots back to normal
        Plotly.relayout('timeline-viz', {
            'xaxis.titlefont.size': 12,
            'xaxis.tickfont.size': 10,
            'margin': { t: 30, b: 60, l: 30, r: 30 }
        });
        
        Plotly.relayout('categories-viz', {
            'xaxis.titlefont.size': 12,
            'yaxis.titlefont.size': 12,
            'xaxis.tickfont.size': 10,
            'yaxis.tickfont.size': 10,
            'margin': { t: 30, b: 60, l: 200, r: 30 }
        });
        
        Plotly.relayout('concept-map-viz', {
            'xaxis.tickfont.size': 10,
            'yaxis.tickfont.size': 10,
            'margin': { t: 30, b: 100, l: 120, r: 30 }
        });
    }
}

/**
 * Set up fullscreen functionality for visualizations
 */
function setupFullscreenViz() {
    const fullscreenBtns = document.querySelectorAll('.viz-fullscreen-btn');
    
    fullscreenBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const vizWrapper = this.closest('.viz-fullscreen-wrapper');
            const vizPanel = this.closest('.viz-panel');
            
            if (!vizWrapper || !vizPanel) return;
            
            // Toggle fullscreen class
            vizPanel.classList.toggle('viz-fullscreen');
            
            // Toggle icon
            const icon = this.querySelector('i');
            if (icon) {
                if (vizPanel.classList.contains('viz-fullscreen')) {
                    icon.classList.remove('fa-expand');
                    icon.classList.add('fa-compress');
                    this.setAttribute('title', 'Exit Fullscreen');
                } else {
                    icon.classList.remove('fa-compress');
                    icon.classList.add('fa-expand');
                    this.setAttribute('title', 'View Fullscreen');
                }
            }
            
            // Find the visualization element
            const vizElement = vizWrapper.querySelector('[id$="-viz"]');
            if (vizElement) {
                // Trigger a resize event to redraw the visualization
                window.dispatchEvent(new Event('resize'));
            }
        });
    });
}
  