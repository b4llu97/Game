import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { listFacts, setFact, deleteFact, Fact } from '../services/api';
import { Plus, Trash2, Edit, Loader2 } from 'lucide-react';

export function FactsManager() {
  const [facts, setFacts] = useState<Fact[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingFact, setEditingFact] = useState<Fact | null>(null);
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');
  const { toast } = useToast();

  useEffect(() => {
    loadFacts();
  }, []);

  const loadFacts = async () => {
    setIsLoading(true);
    try {
      const data = await listFacts();
      setFacts(data);
    } catch (error) {
      toast({
        title: 'Fehler',
        description: error instanceof Error ? error.message : 'Fakten konnten nicht geladen werden',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!newKey.trim() || !newValue.trim()) {
      toast({
        title: 'Fehler',
        description: 'Schlüssel und Wert sind erforderlich',
        variant: 'destructive',
      });
      return;
    }

    try {
      await setFact(newKey, newValue);
      toast({
        title: 'Erfolg',
        description: editingFact ? 'Fakt aktualisiert' : 'Fakt erstellt',
      });
      setIsDialogOpen(false);
      setNewKey('');
      setNewValue('');
      setEditingFact(null);
      loadFacts();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: error instanceof Error ? error.message : 'Fakt konnte nicht gespeichert werden',
        variant: 'destructive',
      });
    }
  };

  const handleEdit = (fact: Fact) => {
    setEditingFact(fact);
    setNewKey(fact.key);
    setNewValue(fact.value);
    setIsDialogOpen(true);
  };

  const handleDelete = async (key: string) => {
    try {
      await deleteFact(key);
      toast({
        title: 'Erfolg',
        description: 'Fakt gelöscht',
      });
      loadFacts();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: error instanceof Error ? error.message : 'Fakt konnte nicht gelöscht werden',
        variant: 'destructive',
      });
    }
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setNewKey('');
    setNewValue('');
    setEditingFact(null);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Fakten-Verwaltung</h2>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              Neuer Fakt
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-gray-900 border-gray-800 text-white">
            <DialogHeader>
              <DialogTitle>{editingFact ? 'Fakt bearbeiten' : 'Neuen Fakt erstellen'}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Schlüssel</label>
                <Input
                  value={newKey}
                  onChange={(e) => setNewKey(e.target.value)}
                  placeholder="z.B. versicherung.gebaeude.summe"
                  disabled={editingFact !== null}
                  className="bg-gray-800 border-gray-700 text-white"
                />
              </div>
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Wert</label>
                <Input
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  placeholder="z.B. 980000 CHF"
                  className="bg-gray-800 border-gray-700 text-white"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <Button variant="outline" onClick={handleDialogClose} className="border-gray-700">
                  Abbrechen
                </Button>
                <Button onClick={handleSave} className="bg-blue-600 hover:bg-blue-700">
                  Speichern
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      ) : facts.length === 0 ? (
        <Card className="bg-gray-800 border-gray-700 p-8 text-center">
          <p className="text-gray-400">Keine Fakten vorhanden. Erstellen Sie einen neuen Fakt.</p>
        </Card>
      ) : (
        <div className="grid gap-3">
          {facts.map((fact) => (
            <Card key={fact.key} className="bg-gray-800 border-gray-700 p-4">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="font-mono text-sm text-blue-400 mb-1">{fact.key}</h3>
                  <p className="text-white">{fact.value}</p>
                  {fact.updated_at && (
                    <p className="text-xs text-gray-500 mt-2">
                      Aktualisiert: {new Date(fact.updated_at).toLocaleString('de-DE')}
                    </p>
                  )}
                </div>
                <div className="flex gap-2 ml-4">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleEdit(fact)}
                    className="text-gray-400 hover:text-white"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleDelete(fact.key)}
                    className="text-gray-400 hover:text-red-400"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
