import { useLogin } from "@/hooks/useLogin";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { loginSchema } from "@/schemas/login.schema";
import type { LoginFormData } from "@/schemas/login.schema";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";


export default function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const { login } = useLogin();

  const onSubmit = async (data: LoginFormData) => {
    try {
        await login(data);
    } catch (error) {
        console.error(error);
        alert("Login failed");
    }
    };

  return (
    <Card className="w-full max-w-md p-8">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold">
          United Staffing
        </h1>

        <p className="mt-2 text-muted-foreground">
          AI Bench Platform
        </p>
      </div>

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="space-y-5"
      >
        <div>
          <Label>Email</Label>

          <Input
            type="email"
            placeholder="name@company.com"
            {...register("email")}
          />

          {errors.email && (
            <p className="mt-1 text-sm text-red-500">
              {errors.email.message}
            </p>
          )}
        </div>

        <div>
          <Label>Password</Label>

          <Input
            type="password"
            placeholder="********"
            {...register("password")}
          />

          {errors.password && (
            <p className="mt-1 text-sm text-red-500">
              {errors.password.message}
            </p>
          )}
        </div>

        <Button
          type="submit"
          className="w-full"
        >
          Sign In
        </Button>
      </form>
    </Card>
  );
}