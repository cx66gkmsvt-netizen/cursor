package main

import (
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/sashabaranov/go-openai"
)

func main() {
	apiKey := os.Getenv("DEEPSEEK_API_KEY")
	if apiKey == "" {
		panic("DEEPSEEK_API_KEY not set")
	}

	client := openai.NewClientWithConfig(openai.ClientConfig{
		BaseURL: "https://api.deepseek.com/v1",
		APIKey:  apiKey,
	})

	r := gin.Default()

	// health check
	r.GET("/api/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	// POST /api/chat { "prompt": "text" }
	r.POST("/api/chat", func(c *gin.Context) {
		var req struct {
			Prompt string `json:"prompt"`
		}
		if err := c.BindJSON(&req); err != nil || req.Prompt == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "invalid prompt"})
			return
		}

		resp, err := client.CreateChatCompletion(
			c,
			openai.ChatCompletionRequest{
				Model: "deepseek-chat",
				Messages: []openai.ChatCompletionMessage{
					{Role: openai.ChatMessageRoleUser, Content: req.Prompt},
				},
				Temperature: 0.7,
			},
		)
		if err != nil {
			c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
			return
		}

		if len(resp.Choices) == 0 {
			c.JSON(http.StatusBadGateway, gin.H{"error": "empty response"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"reply": resp.Choices[0].Message.Content})
	})

	r.Run(":8080")
}

