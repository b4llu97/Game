import { useState, useRef, useEffect } from 'react';
import { Mic, Send, Loader2, Volume2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Toaster } from '@/components/ui/toaster';
import { sendTextQuery, transcribeAudio, synthesizeSpeech, Message } from './services/api';
import { useAudioRecorder } from './hooks/useAudioRecorder';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const { toast } = useToast();
  const { state: recordingState, error: recordingError, startRecording, stopRecording } = useAudioRecorder();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (recordingError) {
      toast({
        title: 'Mikrofon-Fehler',
        description: recordingError,
        variant: 'destructive',
      });
    }
  }, [recordingError, toast]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await sendTextQuery(text, messages);
      const assistantMessage: Message = { role: 'assistant', content: response.response };
      setMessages(prev => [...prev, assistantMessage]);

      const audioBlob = await synthesizeSpeech(response.response);
      playAudio(audioBlob);
    } catch (error) {
      console.error('Error processing message:', error);
      toast({
        title: 'Fehler',
        description: error instanceof Error ? error.message : 'Ein Fehler ist aufgetreten',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleMicClick = async () => {
    if (recordingState === 'idle') {
      await startRecording();
    } else if (recordingState === 'recording') {
      setIsLoading(true);
      try {
        const audioBlob = await stopRecording();
        
        const transcription = await transcribeAudio(audioBlob);
        
        await handleSendMessage(transcription.text);
      } catch (error) {
        console.error('Error processing voice input:', error);
        toast({
          title: 'Fehler',
          description: error instanceof Error ? error.message : 'Spracherkennung fehlgeschlagen',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    }
  };

  const playAudio = (blob: Blob) => {
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audioRef.current = audio;
    
    audio.onplay = () => setIsPlayingAudio(true);
    audio.onended = () => {
      setIsPlayingAudio(false);
      URL.revokeObjectURL(url);
    };
    audio.onerror = () => {
      setIsPlayingAudio(false);
      URL.revokeObjectURL(url);
      toast({
        title: 'Audio-Fehler',
        description: 'Audio konnte nicht abgespielt werden',
        variant: 'destructive',
      });
    };
    
    audio.play().catch(err => {
      console.error('Error playing audio:', err);
      setIsPlayingAudio(false);
      URL.revokeObjectURL(url);
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900/20 to-purple-900/20 flex flex-col">
      <header className="bg-gray-900/50 backdrop-blur-sm border-b border-gray-800 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">J</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Jarvis AI</h1>
            <p className="text-sm text-gray-400">Ihr intelligenter Assistent</p>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-hidden flex flex-col max-w-4xl w-full mx-auto px-4 py-6">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-4">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto">
                  <span className="text-white font-bold text-3xl">J</span>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white mb-2">Willkommen bei Jarvis</h2>
                  <p className="text-gray-400">Stellen Sie eine Frage oder nutzen Sie das Mikrofon</p>
                </div>
              </div>
            </div>
          )}
          
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <Card
                className={`max-w-[80%] p-4 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white border-blue-500'
                    : 'bg-gray-800 text-white border-gray-700'
                }`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
              </Card>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <Card className="bg-gray-800 text-white border-gray-700 p-4">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Jarvis denkt nach...</span>
                </div>
              </Card>
            </div>
          )}
          
          {isPlayingAudio && (
            <div className="flex justify-start">
              <Card className="bg-gray-800 text-white border-gray-700 p-4">
                <div className="flex items-center gap-2">
                  <Volume2 className="w-4 h-4 animate-pulse" />
                  <span className="text-sm">Jarvis spricht...</span>
                </div>
              </Card>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-lg p-4">
          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <Input
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(inputText)}
                placeholder="Nachricht an Jarvis..."
                disabled={isLoading || recordingState !== 'idle'}
                className="bg-gray-800 border-gray-700 text-white placeholder:text-gray-500"
              />
            </div>
            
            <Button
              onClick={() => handleSendMessage(inputText)}
              disabled={!inputText.trim() || isLoading || recordingState !== 'idle'}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Send className="w-4 h-4" />
            </Button>
            
            <Button
              onClick={handleMicClick}
              disabled={isLoading || recordingState === 'processing'}
              className={`${
                recordingState === 'recording'
                  ? 'bg-red-600 hover:bg-red-700 animate-pulse'
                  : 'bg-purple-600 hover:bg-purple-700'
              }`}
            >
              {recordingState === 'processing' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Mic className="w-4 h-4" />
              )}
            </Button>
          </div>
          
          <p className="text-xs text-gray-500 mt-2 text-center">
            {recordingState === 'recording'
              ? 'Aufnahme läuft... Klicken Sie erneut zum Beenden'
              : 'Drücken Sie das Mikrofon für Spracheingabe'}
          </p>
        </div>
      </div>
      
      <Toaster />
    </div>
  );
}

export default App;
