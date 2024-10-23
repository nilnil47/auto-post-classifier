## Development Roadmap

### Production

1. Deploy current code (GPT-based classification) to production and integrate with existing systems.
2. Create a new grading system algorithm. It will be based on the following aspects:
   - Has relevant category
   - How new the post is
   - How much traffic the post has
3. Use LLAMA as the LLM instead of GPT. The reason is mentioned in the reasons section

#### Time Estimation
1. Already fully implemented and waiting for integration with Gil and Emanuel
2. Need to decide where in the system it will be implemented (probably the webapp) and implementation shouldn't be long (probably a week)
3. POC exists, but needs another 4 weeks to fully implement, mainly because of response prompt syntax issues (Neil)

### Research
1. Performance Measurement
   - Develop a method to evaluate model performance
   - Consult with the team to determine the best approach
   - Time estimation: if using current approach, should take 2 weeks. Also depends on how much work other team members will do. Implementation time will be known after this time.

2. Multi-model Support (Two-part implementation)
   a. Model Selection
      - Choose between GPT-4-0-mini, local models, or alternatives from:
        https://www.reddit.com/r/LocalLLaMA/comments/1atww6l/any_opensource_multimodal_llms_out_there/
        gpt4 vision - https://platform.openai.com/docs/guides/vision
   b. Media Crawling Strategy
      - Determine optimal method for media input (direct link vs. extracted media)
      - Conduct research on implementation options
      - Estimated time: should take 2 weeks to understand the best model to use and what its capabilities are

3. Multilingual Support (Optional)
   - Evaluate options: Google Translate API vs. direct LLM input
   - First make a POC to check if it makes a big difference. Implementation will require changing architecture for applying pre-prompt processing, so it can take a while.
   - Time estimation: for POC 2 weeks, and needs to be done after performance estimation implementation.

4. Embedding-based Classification (Optional)
   - Explore classification in embedding space to bypass JSON parsing
   - Assess feasibility and potential benefits
   - Develop regression or classification model for embeddings
   - Time estimation: Variable, based on complexity and developer expertise
