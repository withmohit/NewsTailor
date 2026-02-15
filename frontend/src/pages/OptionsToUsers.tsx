import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

const OptionsToUsers = () => {
  const [categories, setCategories] = useState<string[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSubscribed, setIsSubscribed] = useState<boolean | null>(null);
  const navigate = useNavigate();

  // Get token from localStorage
  const token = localStorage.getItem('access_token');

  // Fetch all available categories
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const res = await axios.get(`${API_BASE}/categories_available`);
        setCategories(res.data);
      } catch (err) {
        setError('Failed to fetch categories.');
      }
    };
    fetchCategories();
  }, []);

  // Fetch user's selected categories
  useEffect(() => {
    const fetchUserCategories = async () => {
      if (!token) return;
      try {
        const res = await axios.get(`${API_BASE}/user-categories`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setSelected(res.data.categories || []);
      } catch (err) {
        setError('Failed to fetch your categories.');
      }
    };
    fetchUserCategories();
  }, [token]);

  // Check subscription status on mount
  useEffect(() => {
    const checkSubscription = async () => {
      if (!token) return;
      try {
        const res = await axios.get(`${API_BASE}/unsubscribe`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setIsSubscribed(res.data?.isSubscribed ?? true); // assume true if not present
      } catch (err) {
        setIsSubscribed(true); // fallback: assume subscribed
      }
    };
    checkSubscription();
  }, [token]);

  const toggleCategory = useCallback((cat: string) => {
    setSelected((prev) => prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]);
  }, []);

  const handleUpdate = async () => {
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/update-categories`, { categories: selected }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSuccess('Categories updated!');
    } catch (err) {
      setError('Failed to update categories.');
    } finally {
      setLoading(false);
    }
  };

  const handleUnsubscribe = async () => {
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      if (isSubscribed) {
        await axios.post(`${API_BASE}/unsubscribe`, {}, {
          headers: { Authorization: `Bearer ${token}` },
        });
        localStorage.removeItem('access_token');
        setSuccess('You have been unsubscribed.');
        setIsSubscribed(false);
        setTimeout(() => navigate('/'), 1500);
      } else {
        await axios.post(`${API_BASE}/subscribe`, {}, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setSuccess('You have been subscribed again.');
        setIsSubscribed(true);
      }
    } catch (err) {
      setError(isSubscribed ? 'Failed to unsubscribe.' : 'Failed to subscribe.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem('access_token');
    navigate('/signin');
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar />
      <main className="container mx-auto flex max-w-md flex-col px-4 py-16">
        <h1 className="text-2xl font-bold mb-4">Account Options</h1>
        {error && <div className="text-sm text-destructive mb-2">{error}</div>}
        {success && <div className="text-sm text-green-600 mb-2">{success}</div>}
        <Button variant={isSubscribed ? "destructive" : "default"} className="mb-6" onClick={handleUnsubscribe} disabled={loading}>
          {isSubscribed === null ? '...' : isSubscribed ? 'Unsubscribe' : 'Subscribe Again'}
        </Button>
        <div className="space-y-2 mb-4">
          <div className="font-semibold">Your News Categories</div>
          <div className="flex flex-wrap gap-2 pt-1">
            {categories.map((cat) => (
              <Badge
                key={cat}
                variant={selected.includes(cat) ? "default" : "outline"}
                className="cursor-pointer select-none"
                onClick={() => toggleCategory(cat)}
              >
                {cat}
              </Badge>
            ))}
          </div>
        </div>
        <Button className="mb-6" onClick={handleUpdate} disabled={loading}>
          {loading ? 'Updating...' : 'Update Categories'}
        </Button>
        <Button variant="outline" onClick={handleSignOut}>
          Sign Out
        </Button>
      </main>
      <Footer />
    </div>
  );
};

export default OptionsToUsers;
