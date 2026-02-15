import { useState, useEffect, useCallback, useMemo } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import axios from 'axios';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from "@/components/ui/dialog";

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

const SignUp = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [OTP, setOTP] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [showOtpSection, setOptSection] = useState(false);

  const [loadingCategories, setLoadingCategories] = useState(false);
  const [loadingVerify, setLoadingVerify] = useState(false);
  const [loadingSubmit, setLoadingSubmit] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMessage, setDialogMessage] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const fetchCategories = async () => {
      setLoadingCategories(true);
      try {
        const response = await axios.get(`${API_BASE}/categories_available`, { signal: controller.signal });
        const data = response?.data;
        setCategories(Array.isArray(data) ? data : []);
      } catch (err: any) {
        if (err?.name === 'CanceledError' || err?.message === 'canceled') return;
        console.error("Error fetching categories:", err);
        setCategories([]);
      } finally {
        setLoadingCategories(false);
      }
    };

    fetchCategories();
    return () => controller.abort();
  }, []);

  const toggleCategory = useCallback((cat: string) => {
    setSelected((prev) => (prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]));
  }, []);

  const canRequestVerification = useMemo(() => {
    return name.trim() !== '' && email.trim() !== '' && password.trim() !== '';
  }, [name, email, password]);

  const validate_email = useCallback(async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError(null);
    if (!canRequestVerification) {
      setError('Name, email and password are required to verify.');
      return;
    }

    setLoadingVerify(true);
    try {
      const res = await axios.post(`${API_BASE}/register`, {
        name,
        email,
        password,
        categories: selected,
      });

      const status = Boolean(res?.data?.status);
      setOptSection(status);
      if (status === false) {
        setDialogMessage(res?.data?.message ?? 'Verification requested');
        setDialogOpen(true);
      }
      console.log(res?.data?.message ?? 'verification requested');
    } catch (err) {
      console.error('Error requesting verification:', err);
      setError('Unable to request verification. Please try again.');
    } finally {
      setLoadingVerify(false);
    }
  }, [name, email, password, selected, canRequestVerification]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!OTP.trim()) {
      setDialogMessage('Please enter the OTP.');
      setDialogOpen(true);
      return;
    }

    setLoadingSubmit(true);
    try {
      const res = await axios.post(`${API_BASE}/verify-otp`, { email, OTP });
      console.log(res.data);
      // Optionally handle redirect or show success message here
    } catch (err) {
      console.error('Error verifying OTP:', err);
      setError('OTP verification failed.');
    } finally {
      setLoadingSubmit(false);
    }
  }, [ email, showOtpSection]);

  const badges = useMemo(() => {
    return categories.map((cat) => (
      <Badge
        key={cat}
        variant={selected.includes(cat) ? "default" : "outline"}
        className="cursor-pointer select-none"
        onClick={() => toggleCategory(cat)}
      >
        {cat}
      </Badge>
    ));
  }, [categories, selected, toggleCategory]);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar />
      <main className="container mx-auto flex max-w-md flex-col px-4 py-16">
        <h1 className="text-2xl font-bold">Create your account</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Already have an account?{' '}
          <Link to="/signin" className="text-primary underline underline-offset-4">
            Sign in
          </Link>
        </p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-5">
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required />
          </div>

          <div className="space-y-2">
            <Label>News Categories</Label>
            <p className="text-xs text-muted-foreground">Click to add or remove topics you're interested in.</p>
            <div className="flex flex-wrap gap-2 pt-1">
              {loadingCategories ? <div className="text-sm text-muted-foreground">Loading...</div> : badges}
            </div>
          </div>

          {error && <div className="text-sm text-destructive">{error}</div>}

          <Button className="w-full" type="button" onClick={validate_email} disabled={loadingVerify || !canRequestVerification} aria-disabled={loadingVerify || !canRequestVerification}>
            {loadingVerify ? 'Sending...' : 'Verify Your Email'}
          </Button>

          {showOtpSection && (
            <>
              <div className="space-y-2">
                <Label htmlFor="OTP">OTP</Label>
                <Input id="otp" value={OTP} onChange={(e) => setOTP(e.target.value)} placeholder="4 digit otp" required/>
              </div>
              <Button type="submit" className="w-full" disabled={loadingSubmit}>
                {loadingSubmit ? 'Verifying...' : 'Sign Up'}
              </Button>
            </>
          )}
        </form>
      </main>
      <Footer />
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Registration Error</DialogTitle>
            <DialogDescription>{dialogMessage}</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose asChild>
              <Button onClick={() => setDialogOpen(false)}>Close</Button>
            </DialogClose>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default SignUp;
