1. run the current code in the production and intergrate to the our systems. beacuse there is problem with the current load balancing.
check the request to 50 each time - going to be implemented by gil.

2. create a way to measure the performace of the model. we need to think of a way to astimated the model performance. want to console with the team what is the best way to do so. time astimation will be decided after. need to think together on a good way to do it.

3. compare the performace to a local llm to check if we can use this to reduce costs?

4. add multi-model support. this has 2 parts.
1 - choose the model (can be gpt-4-0-mini or another local one or one from:
https://www.reddit.com/r/LocalLLaMA/comments/1atww6l/any_opensource_multimodal_llms_out_there/)
2 - understand which type of cralling is needed to use the meida - for example, if it possible to give the model the link
to the post or we need to extract the media from the post, and give it seperatly

