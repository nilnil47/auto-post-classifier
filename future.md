## Development Roadmap

### production

   1. Deploy current code (GPT based classification)to production and integrate with existing systems.
   2. create a new grading system algorithem. its will be based on the following aspects:
      has relevant category
      how new the post is
      how traffic the post have
   3. Use LLAMA as the LLM instead of GPT. The reason is mentioned in the reasons section
   

#### time asstimation
1. already fully implemented and wait for intergration with Gil and Emanuel
2. needed to decide where in the system it will be implemented (probably the webapp) and implemenation shoudnt be long (probably week)
3. poc is exist, but need another 4 weeks to fully implement, mainy because respose prompt syntax issues (Neil)
      
### reaserch
1. Performance Measurement
   - Develop a method to evaluate model performance
   - Consult with the team to determine the best approach
   - Time estimation: if using current approch, shoud take 2 weeks. also depends of how much works other team memebers will do. implementation time will be known after this time.

2. Multi-model Support (Two-part implementation)
   a. Model Selection
      - Choose between GPT-4-0-mini, local models, or alternatives from:
        https://www.reddit.com/r/LocalLLaMA/comments/1atww6l/any_opensource_multimodal_llms_out_there/
	gpt4 vision - https://platform.openai.com/docs/guides/vision
   b. Media Crawling Strategy
      - Determine optimal method for media input (direct link vs. extracted media)
      - Conduct research on implementation options
      - Estimated time: shoud take 2 weeks to understand the best model to use and what is the cababilities

3. Multilingual Support (Optional)
   - Evaluate options: Google Translate API vs. direct LLM input
   - first make a poc to check if it doing a big difference. implemnation will be      require to change aritechture for applaying pre promot processing so can take a while.
   - Time estimation: for poc 2 weeks, and needs to be done after profermence asstimation implementation.

4. Embedding-based Classification (Optional)
   - Explore classification in embedding space to bypass JSON parsing
   - Assess feasibility and potential benefits
   - Develop regression or classification model for embeddings
   - Time estimation: Variable, based on complexity and developer expertise