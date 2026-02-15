import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

const SignIn = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try{
      const res = await axios.post(`${API_BASE}/signin`,{email, password});
      console.log(res.data)
      // save access token to localStorage (try common fields)
      const token = res?.data?.access_token ?? res?.data?.token ?? res?.data?.accessToken;
      if (token) {
        localStorage.setItem('access_token', token);
        // also set default Authorization header for future axios requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        navigate('/optionstousers');
      }
      console.log("Sign in:", { email, password });
    }
    catch (err){
      console.error(err);
      setError('Sign in failed. Please check your credentials and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar />
      <main className="container mx-auto flex max-w-md flex-col px-4 py-16">
        <h1 className="text-2xl font-bold">Sign in</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Don't have an account?{" "}
          <Link to="/signup" className="text-primary underline underline-offset-4">
            Sign up
          </Link>
        </p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-5">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required />
          </div>
          {error && <div className="text-sm text-destructive">{error}</div>}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>
      </main>
      <Footer />
    </div>
  );
};

export default SignIn;
