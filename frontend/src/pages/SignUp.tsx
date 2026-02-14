import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import axios from 'axios';

const SignUp = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [OTP, setOTP] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [categories, setCategories] = useState<string[]>([]); // initially empty
  const [showOtpSection, setOptSection] = useState(false)
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/categories_available");
        console.log(response);
        setCategories(response.data);
      } catch (error) {
        console.error("Error fetching categories:", error);
      }
    };

    fetchCategories();
  }, []);

  const toggleCategory = (cat: string) => {
    setSelected((prev) =>
      prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    axios.post('http://127.0.0.1:8000/verify-otp',{
      email,
      OTP
    })
     .then(res => {
      console.log(res.data)
  })
    console.log('verified :' +email);
  };

    const validate_email = (e: React.FormEvent) => {
    e.preventDefault();
    axios.post('http://127.0.0.1:8000/register',{
      name,
      email,
      password,
      categories: selected
    })
     .then(res => {
      console.log(res.data.message)
      setOptSection(res.data.status)
  })
    console.log("Sign up:", { name, email, password, categories: selected });
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar />
      <main className="container mx-auto flex max-w-md flex-col px-4 py-16">
        <h1 className="text-2xl font-bold">Create your account</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Already have an account?{" "}
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

            <Button className="w-full" type="button" onClick={validate_email}>
            Verify Your Email
            </Button>
            {showOtpSection && (
            <>
              <div className="space-y-2">
              <Label htmlFor="OTP">OTP</Label>
              <Input id="otp" value={OTP} onChange={(e) => setOTP(e.target.value)} placeholder="4 digit otp" required />
              </div>
              <Button type="submit" className="w-full">
              Sign Up
              </Button>
            </>
            )}
          
        </form>
      </main>
      <Footer />
    </div>
  );
};

export default SignUp;
