import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import json
import os
from datetime import datetime
from telegram import Update, Message, User, Chat, Document, PhotoSize
from telegram.ext import ContextTypes
import bot


class TestTelegramBot(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.mock_user = Mock(spec=User)
        self.mock_user.id = 123456789
        self.mock_user.username = "testuser"
        self.mock_user.first_name = "Test"
        self.mock_user.last_name = "User"
        
        self.mock_chat = Mock(spec=Chat)
        self.mock_chat.id = 987654321
        
        self.mock_message = Mock(spec=Message)
        self.mock_message.message_id = 1
        self.mock_message.text = "Hello, bot!"
        self.mock_message.chat_id = self.mock_chat.id
        self.mock_message.date = datetime.now()
        self.mock_message.reply_text = AsyncMock()
        
        self.mock_update = Mock(spec=Update)
        self.mock_update.effective_user = self.mock_user
        self.mock_update.message = self.mock_message
        
        self.mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        self.mock_context.bot = Mock()
        self.mock_context.bot.set_message_reaction = AsyncMock()

    def test_environment_variables_required(self):
        """Test that required environment variables are checked"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as cm:
                import importlib
                importlib.reload(bot)
            self.assertIn("TELEGRAM_BOT_TOKEN", str(cm.exception))

    @patch('bot.requests.post')
    def test_send_to_n8n_success(self, mock_post):
        """Test successful n8n webhook call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"status": "success"}'
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        test_data = {"test": "data"}
        result = bot.send_to_n8n(test_data)
        
        mock_post.assert_called_once_with(bot.N8N_WEBHOOK_URL, json=test_data, timeout=10)
        self.assertEqual(result, {"status": "success"})

    @patch('bot.requests.post')
    def test_send_to_n8n_failure(self, mock_post):
        """Test failed n8n webhook call"""
        mock_post.side_effect = Exception("Connection error")
        
        test_data = {"test": "data"}
        result = bot.send_to_n8n(test_data)
        
        self.assertIsNone(result)


class TestBotHandlers(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for handler tests"""
        self.mock_user = Mock(spec=User)
        self.mock_user.id = 123456789
        self.mock_user.username = "testuser"
        self.mock_user.first_name = "Test"
        self.mock_user.last_name = "User"
        
        self.mock_chat = Mock(spec=Chat)
        self.mock_chat.id = 987654321
        
        self.mock_message = Mock(spec=Message)
        self.mock_message.message_id = 1
        self.mock_message.chat_id = self.mock_chat.id
        self.mock_message.date = datetime.now()
        self.mock_message.reply_text = AsyncMock()
        
        self.mock_update = Mock(spec=Update)
        self.mock_update.effective_user = self.mock_user
        self.mock_update.message = self.mock_message
        
        self.mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        self.mock_context.bot = Mock()
        self.mock_context.bot.set_message_reaction = AsyncMock()

    @patch('bot.send_to_n8n')
    def test_start_command_handler(self, mock_send_to_n8n):
        """Test /start command handler"""
        mock_send_to_n8n.return_value = {"status": "success"}
        
        async def run_test():
            await bot.start(self.mock_update, self.mock_context)
            
            # Check that n8n was called with correct data
            mock_send_to_n8n.assert_called_once()
            call_args = mock_send_to_n8n.call_args[0][0]
            
            self.assertEqual(call_args["type"], "command")
            self.assertEqual(call_args["command"], "start")
            self.assertEqual(call_args["user_id"], self.mock_user.id)
            self.assertEqual(call_args["username"], self.mock_user.username)
            
            # Check that welcome message was sent
            self.mock_message.reply_text.assert_called_once()
            reply_text = self.mock_message.reply_text.call_args[0][0]
            self.assertIn("Hello!", reply_text)
        
        asyncio.run(run_test())

    @patch('bot.send_to_n8n')
    def test_handle_message_with_reply(self, mock_send_to_n8n):
        """Test message handler when n8n returns a reply"""
        self.mock_message.text = "Test message"
        mock_send_to_n8n.return_value = {"reply": "Bot response"}
        
        async def run_test():
            await bot.handle_message(self.mock_update, self.mock_context)
            
            # Check that n8n was called with correct data
            mock_send_to_n8n.assert_called_once()
            call_args = mock_send_to_n8n.call_args[0][0]
            
            self.assertEqual(call_args["type"], "message")
            self.assertEqual(call_args["text"], "Test message")
            self.assertEqual(call_args["user_id"], self.mock_user.id)
            
            # Check that reply was sent
            self.mock_message.reply_text.assert_called_once_with("Bot response")
        
        asyncio.run(run_test())

    @patch('bot.send_to_n8n')
    def test_handle_message_with_reaction(self, mock_send_to_n8n):
        """Test message handler when n8n doesn't return a reply"""
        self.mock_message.text = "Test message"
        mock_send_to_n8n.return_value = {"status": "received"}
        
        async def run_test():
            await bot.handle_message(self.mock_update, self.mock_context)
            
            # Check that reaction was set instead of reply
            self.mock_context.bot.set_message_reaction.assert_called_once_with(
                chat_id=self.mock_message.chat_id,
                message_id=self.mock_message.message_id,
                reaction="👍"
            )
            self.mock_message.reply_text.assert_not_called()
        
        asyncio.run(run_test())

    @patch('bot.send_to_n8n')
    def test_handle_photo(self, mock_send_to_n8n):
        """Test photo handler"""
        mock_photo = Mock(spec=PhotoSize)
        mock_photo.file_id = "photo123"
        self.mock_message.photo = [mock_photo]
        self.mock_message.caption = "Test photo"
        
        mock_send_to_n8n.return_value = {"status": "received"}
        
        async def run_test():
            await bot.handle_photo(self.mock_update, self.mock_context)
            
            # Check that n8n was called with correct data
            mock_send_to_n8n.assert_called_once()
            call_args = mock_send_to_n8n.call_args[0][0]
            
            self.assertEqual(call_args["type"], "photo")
            self.assertEqual(call_args["photo_file_id"], "photo123")
            self.assertEqual(call_args["caption"], "Test photo")
            
            # Check that reaction was set
            self.mock_context.bot.set_message_reaction.assert_called_once()
        
        asyncio.run(run_test())

    @patch('bot.send_to_n8n')
    def test_handle_document(self, mock_send_to_n8n):
        """Test document handler"""
        mock_document = Mock(spec=Document)
        mock_document.file_id = "doc123"
        mock_document.file_name = "test.pdf"
        mock_document.mime_type = "application/pdf"
        
        self.mock_message.document = mock_document
        self.mock_message.caption = "Test document"
        
        mock_send_to_n8n.return_value = {"reply": "Document received"}
        
        async def run_test():
            await bot.handle_document(self.mock_update, self.mock_context)
            
            # Check that n8n was called with correct data
            mock_send_to_n8n.assert_called_once()
            call_args = mock_send_to_n8n.call_args[0][0]
            
            self.assertEqual(call_args["type"], "document")
            self.assertEqual(call_args["document_file_id"], "doc123")
            self.assertEqual(call_args["document_name"], "test.pdf")
            self.assertEqual(call_args["document_mime_type"], "application/pdf")
            
            # Check that reply was sent
            self.mock_message.reply_text.assert_called_once_with("Document received")
        
        asyncio.run(run_test())


class TestBotIntegration(unittest.TestCase):
    """Integration tests for the bot"""
    
    @patch('bot.TELEGRAM_BOT_TOKEN', 'test_token')
    @patch('bot.N8N_WEBHOOK_URL', 'http://test.webhook')
    @patch('bot.Application')
    def test_main_function_setup(self, mock_application_class):
        """Test that main function sets up the bot correctly"""
        mock_app = Mock()
        mock_application_class.builder.return_value.token.return_value.build.return_value = mock_app
        
        # Mock the run_polling method to avoid actually starting the bot
        mock_app.run_polling = Mock()
        
        bot.main()
        
        # Check that handlers were added
        self.assertEqual(mock_app.add_handler.call_count, 4)
        
        # Check that bot starts polling
        mock_app.run_polling.assert_called_once()


def run_tests():
    """Run all tests"""
    # Set environment variables for testing
    os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token_123'
    os.environ['N8N_WEBHOOK_URL'] = 'http://localhost:5678/webhook/test'
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTelegramBot))
    suite.addTests(loader.loadTestsFromTestCase(TestBotHandlers))
    suite.addTests(loader.loadTestsFromTestCase(TestBotIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)